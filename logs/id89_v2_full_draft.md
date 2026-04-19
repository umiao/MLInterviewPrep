# Search & Retrieval Systems (L5 Concepts & Design Spine)

这一题的外皮是"给我设计一个搜索引擎"——Google 网页搜索、Amazon 商品搜索、LinkedIn People Search、Slack 消息搜索、Notion 企业知识库都能套。与 id=198 Real-Time Recommendation 不同，本题的重心不是"把一套 end-to-end 服务拆分讲完"，而是"把搜索系统的多阶段漏斗与每层算法候选 + 工具链讲透"：**Query Understanding** (查询理解) 用哪类模型、L0/L1/L2 三级检索各自的默认方案与 why-not、**Inverted Index** (倒排索引) 怎么分片分层、新鲜度怎么做增量、精排在 **LambdaMART** 与 **Cross-Encoder** (交叉编码器) 之间如何取舍。简言之 id=198 回答"怎么把这套系统在 100M 用户下部署"，id=89 回答"搜索系统的每一层有哪些可选建模工具、各自的适用边界是什么"。本题考点不是"跑一个 BM25 baseline"，而是"能不能把 BM25 / Bi-Encoder / Cross-Encoder / ColBERT / LambdaMART / HNSW / IVF-PQ / Lucene / Vespa 这些工具在同一条时间轴上摆清楚并给出可落地的切换触发条件"。

## Prerequisites

→ 参见 [id=18 System Design Framework](/kg?node=n18)、[id=90 Recommendation Systems](/kg?node=n90)、[id=198 Real-Time Recommendation](/kg?node=n198)

先读 id=18 的理由是：L5 范式与 Appendix A.1.v2 Writing Discipline (每个技术选择都要 Pick + ≥3 候选 + why-not + 切换条件 + 常见追问五元组) 是本题所有 deep dive 的评分标尺。再读 id=90 的理由是：推荐系统的多阶段漏斗与搜索几乎同构——区别只在 id=90 的 retrieval 是 user × item 内积，本题的 retrieval 是 query × document 倒排 + 稠密向量双路。读者应对 **Best Matching 25** (BM25, 最佳匹配25)、**Approximate Nearest Neighbor** (ANN, 近似最近邻)、**Hierarchical Navigable Small World** (HNSW, 分层可导航小世界图)、**Inverted File with Product Quantization** (IVF-PQ, 倒排文件+乘积量化)、**Normalized Discounted Cumulative Gain** (NDCG, 归一化折损累积增益)、**Bi-Encoder** (双编码器) 与 **Cross-Encoder** (交叉编码器) 的差别、**Learning to Rank** (LTR, 排序学习) 三范式 Pointwise / Pairwise / Listwise 的适用边界都应有基础认识，否则容易在 §4b 检索层与 §4c 排序层的对比环节卡住。

## 1. Requirements Clarification (5m)

需求澄清不是把题面复读一遍，而是要把五个必问 (规模、读写、延迟、一致性、跨地域) 答清楚，每一问的答案都会在后面某个架构决策里被引用。目标是离开这一节时，面试官能预判到"这套系统的瓶颈落在倒排扇出与精排 Cross-Encoder 推理、强一致只出现在付费广告 slot 分配与 A/B 分桶一瞬、跨 region 只做异步容灾不做同步检索"。

**Functional requirements (功能需求)** 主流程是用户请求搜索 → 查询理解 → 多路检索 → 融合 → 精排 → 重排 → 返回列表；辅流程含点击/停留/SAT 事件回流、实时索引更新 (10 分钟内可召回)、文档入库审核、同义词词典维护、自动补全、相关查询推荐；平台级功能含 personalization、冷启动 slot 配额、广告与自然结果混排、facet / filter 侧边栏、知识卡片插入。这些功能归成四组——查询理解、检索、排序、索引维护——后续 deep dive 按这四组展开。

**Non-functional requirements (非功能需求)** 规模取 Google/Pinterest 级：文档库 10B (10⁹)、**Queries Per Second** (QPS, 每秒查询数) 峰值 50K、每秒倒排扫描 50K × 1000 = 50M postings/s、精排调用 50K × 100 = 5M invocations/s；延迟端到端 p99 < 100ms 分摊到 Query Understanding 10ms + L0 倒排 20ms + L1 稠密 30ms + L2 精排 20ms + 重排 10ms + 序列化 10ms；特征查询 p99 < 5ms；一致性除广告 slot 分配与 A/B 分桶强一致外其他全 eventual；可用性月度 99.95% 约 22 分钟 budget；新鲜度新闻/社交 < 1 分钟、商品 < 10 分钟、网页 < 1 小时分层处理。

**Out-of-scope (排除项)** 广告拍卖 (另开 id=91)、深入内容审核 (spam / NSFW)、crawl 抓取调度、前端渲染、多模态 image / video search 的 vision backbone 预训练。排除不是忽略而是主动声明——面试官问广告拍卖时我知道这超范围、可以明确"广告层本篇不深挖"。

**必问五问的本题答**：Q1 规模 文档 10B、QPS 50K、精排 5M invocations/s；Q2 读写 读远大于写，单请求 > 1M postings 扫描、索引写 5-50K docs/s；Q3 延迟 端到端 p99 < 100ms 是整篇最硬的数字；Q4 一致性 A/B 分桶与广告 slot 强一致、索引更新 eventual；Q5 地域 多 region 本地检索 + 全球同步文档库、跨 region 只异步容灾。这五个答案是后面每一节的锚点。

这一节 takeaway：所有后续决策从这五问推出，任何选型都能反向追溯到需求条款——这是 L5 与 L4 的分水岭。

## 2. Capacity Estimation (5m)

容量估算这一节的目的不是炫耀算术，而是给每一个建模/基础设施决策找实在的瓶颈锚点。按查询扇出 → 倒排索引 → 稠密向量 → 事件总线四条链路走一遍，每段除了给数字还给出对应的选型块。

### 查询扇出链 (50K QPS × 1000 postings = 50M postings/s)

50K QPS × 每查询平均扫描 1000 个 postings = 50M postings/s 全局扫描压力。这个数字把倒排检索引擎直接压进"必须跨 shard 并行扫描 + mmap + SIMD"的硬件边界。

倒排检索引擎我选 **Elasticsearch** (Lucene-based)，因为它 Lucene 内核倒排实现稳定十年、mmap + SIMD 加速 posting list 扫描、分布式 scatter-gather 天然集成、运维工具链成熟。候选一是 **Apache Lucene 裸用**——延迟更低但缺分布式协调，Lucene 裸用更合适的位置是单机嵌入式搜索，不用。候选二是 **Vespa**——稀疏倒排 + 稠密向量 + LTR 统一 runtime、Pinterest 验证，但运维工具链不如 Elasticsearch 成熟，Vespa 更合适的位置是稀疏/稠密/LTR 强耦合的 big-tech 内核场景。候选三是 **Apache Solr**——Lucene 早期周边，但 SolrCloud 稳定性问题多，Solr 更合适的位置是历史遗留企业搜索，淘汰。切换触发：跨引擎协调延迟 > 20ms 时迁 Vespa；文档量 < 10M 时退回 Lucene 裸用。

> **常见追问**:
> 1. "Elasticsearch 写入峰值会阻塞读吗？" —— 走独立 ingest node 池 + 异步 refresh_interval=5s、读路径走 search node 不被 flush 影响。
> 2. "倒排索引怎么分片？" —— 按 doc_id hash 默认 20-40 shards、避免 term skew 把热门词压爆单 shard。
> 3. "查询零结果率高怎么办？" —— 查询理解补拼写纠错 + 同义词扩展 + 宽松匹配兜底、zero-result rate 是核心 SLO。

### 倒排索引层 (10B docs × 500 terms = 20 TB postings)

文档 10B × 每文档平均 500 tokens × 4B (doc_id) = **~20 TB 倒排 postings**；每 shard ~500 GB、需 ~40 shards 才能塞进 64GB 内存机型。这个 20TB 把 **Sharding** (分片) 策略直接压到"必须按 doc_id hash + 副本"的硬件边界。

分片策略我选 **按 doc_id hash 的 document-partitioned index**——每 shard 放全量 term dictionary + 自己那份 doc 的 postings，因为每 shard 扫描量均衡、加新机器不用 rebalance term space、Google / Elasticsearch 默认模式。候选一是 **term-partitioned index**——按 term hash 分 shard，但 AND 多 terms 需多机 join + 长 posting list 的 hot term 压垮单机，term-partitioned 更合适的位置是少 term 专有名词索引，淘汰。候选二是 **topic-partitioned**——按 category 切 shard，但跨 topic 查询需并查 + topic 不均衡负载倾斜 10×，topic-partitioned 更合适的位置是 vertical search (LinkedIn People)，不用。候选三是 **document-partitioned + 3× Replication** (副本)——可用性 + 读吞吐双赢，Sharding + Replication 标配增强，保留默认。切换触发：hot-shard 热点 (p99 分片延迟差 > 3×) 时评估 term-partitioned 混合；垂直化到单一 domain 时尝试 topic-partitioned。

> **常见追问**:
> 1. "分片数怎么定？" —— 单 shard 目标 10-50 GB (过大 segment merge 慢)、单机承载 2-4 shards 留内存头、20 TB / 500 GB per shard = 40 shards。
> 2. "**Scatter-Gather** (分发-汇聚) tail latency 怎么压？" —— backup request (发两份取先到)、straggler 监测 + reroute、p99 打 p999 差从 5× 压到 1.5×。
> 3. "新 shard 数据迁移阻塞写入吗？" —— Elasticsearch 的 shrink / split API 支持在线 rebalance、配 throttle 限速避免抢 IO。

### 稠密向量层 (10B × 128d = 5 TB embedding)

10B 文档 × 128d × 4B = **5 TB embedding**、单机内存完全不够；按 128 shards 分切、每 shard 40GB 可塞 64GB 机型。这个 5TB 把 ANN 选型直接压到"必须量化 + 分片"的硬件边界。

稠密 ANN 索引我选 **FAISS IVF-PQ** 128 shards，因为倒排 + 乘积量化内存只要 1/8、10B × 128d 压到 ~700 GB、recall@100 ≈ 0.90 可接受。候选一是 **HNSW** (hnswlib)——图结构 recall@100 ≈ 0.95 更高 + 支持 online insert，但 10B 规模图索引 ~4 TB 内存压力大，HNSW 更合适的位置是 100M-1B docs 中规模召回 (id=90 推荐 500M items 场景刚好)，本题 10B 规模不用。候选二是 **ScaNN** (Google)——各向异性量化吞吐高 2×，但 K8s 部署成本高 + 跨云兼容性弱，ScaNN 更合适的位置是 GCP Vertex AI 原生栈，淘汰。候选三是 **Milvus**——K8s-native + 多租户，但延迟比 FAISS 多 10-15ms + 运维复杂，Milvus 更合适的位置是多业务线共用向量基础设施。候选四是 **Pinecone** (SaaS)——运维 0 成本，但 10B 向量 SaaS 账单月 100K+ 美元，Pinecone 更合适的位置是 < 1K QPS 早期 MVP。切换触发：recall > 0.95 且文档规模 < 1B 时迁 HNSW。

> **常见追问**:
> 1. "**IVF-PQ** 召回损失怎么补？" —— two-stage rerank (PQ 粗选 top-1000 后、原始 float 向量精算 top-100、recall 回升 0.95)。
> 2. "稠密和稀疏用同一套 embedding 吗？" —— 不，稀疏是 term-level token + IDF 权重，稠密是 **Dense Retrieval** (稠密检索) 或 **Dense Passage Retrieval** (DPR) token-level 向量。
> 3. "增量索引怎么做？" —— 新文档走 delta index (小 FAISS 分片、每小时 merge 回主索引)、主索引日级全量 rebuild 兜底。

### 事件总线 + 训练存储 (200 MB/s → 17 TB/day)

搜索行为事件 50K QPS × 4 events × 1KB ≈ **200 MB/s**、日 17 TB。事件总线我选 **Kafka 128 partitions**，因为单 partition 20-30 MB/s、128 partition > 2.5 GB/s 留 10× headroom、exactly-once + 消费组隔离让特征回流与训练 sink 互不干扰。候选一是 **Apache Pulsar**——多租户隔离好，但运维复杂 + 社区规模 1/5，Pulsar 更合适的位置是 SaaS 多租户场景，不用。候选二是 **AWS Kinesis**——托管省运维，但单 shard 1 MB/s 上限低，Kinesis 更合适的位置是 Lambda-only 栈，淘汰。候选三是 **RabbitMQ**——事务语义丰富但吞吐 200 MB/s 无法承载 2 GB/s，RabbitMQ 更合适的位置是 RPC-like 场景。切换触发：多团队强隔离 sink 时迁 Pulsar。训练数据存储走 **S3 + Parquet + Iceberg**；替代的 **HDFS** 运维重、**Delta Lake** 绑 Databricks、**BigQuery** 扫描计费不可控，都不默认。

这一节 takeaway：50M postings/s 推出 Elasticsearch/Lucene、20TB 倒排推出 document-partitioned + 40 shards、5TB embedding 推出 FAISS IVF-PQ 128 shards、17TB/day log 推出 Kafka 128p + S3 Iceberg——这四组数字把 §3 的服务拆分边界画好。

## 3. High-Level Architecture (15m)

架构这一节要讲清两件事：服务怎么切——按漏斗层 + SLA 切，而不是按业务域 (Document / User / Query) 切；数据怎么流——查询到结果的端到端 fan-out 结构要让面试官一眼画出来。切分逻辑不是审美偏好而是 §2 数字直接推出：倒排 L0 扫描层 CPU-bound、稠密 L1 ANN 查询内存-bound、精排 L2 Cross-Encoder 推理 GPU-bound，三者 SLA / 硬件特性完全不同，不能共线程池。

服务拆分策略我选 **按漏斗层 + SLA 切分**：Query Understanding / Retrieval (L0 倒排 + L1 稠密) / Ranker (L2 精排) / Re-Rank (多样性 + 个性化 + 广告混排) / Index Service / Feature Store。因为每层 SLA 独立允许独立扩缩容、独立 A/B、独立模型热加载；塞进一个 "Search Service" 则任一层流量飙升会级联打崩整条链路。候选一是 **按业务域切分** (Document / Query / User)——界面实体抄到后端、忽略 SLA 差异 + 热冷门 QPS 差 100× 互相拖垮，淘汰。候选二是 **按数据管道切分** (Ingest / Search / Rank)——比业务域合理但把 L0/L1/L2 打包成单一 Search 块仍让倒排 CPU 与 Cross-Encoder GPU 耦合，数据管道切分更合适的位置是纯 ETL。候选三是 **按客户端切分** (Mobile / Desktop / API)——只能复制链路不能解耦计算，按客户端切分更合适的位置是 Edge CDN / Gateway 层，不用。切换触发：两层 SLA 趋同时可合并；引入 **LLM** (Large Language Model, 大语言模型) re-rank 后 p99 拉到 500ms 必须再切一层。

> **常见追问**:
> 1. "L0 倒排、L1 稠密、L2 精排可以共用同一个模型吗？" —— 不行，L0 BM25 是手算评分、L1 Bi-Encoder 是预计算 embedding + ANN、L2 Cross-Encoder 是联合编码，目标函数与部署硬件都不同。
> 2. "Query Understanding 放进 Retrieval Service 行吗？" —— 短期可合并省 RPC，但查询重写 / 意图分类模型更新频率 (天级) 与检索索引 (小时级) 差 10×，独立服务便于灰度。
> 3. "Personalization 算独立服务吗？" —— 算，个性化特征查询接 Feature Store，Re-Rank Service 消费，放独立服务便于审计 + 合规下线。

端到端数据流：用户查询进 Gateway → Query Understanding Service 做拼写纠错 + 意图识别 + 查询扩展 → A/B Service 决定本次桶 → Retrieval Service 同时发 L0 倒排 (BM25) 和 L1 稠密 (Bi-Encoder + FAISS) → **Reciprocal Rank Fusion** (RRF, 倒数排名融合) 合并到 top-1000 → Ranker Service 用 LambdaMART 精排到 top-100 → Re-Rank Service 叠 Cross-Encoder + 多样性 + 个性化 + 广告 slot → 返回 top-10。关键是每层独立 fallback：查询理解挂了退回 raw query；稠密路挂了退回纯倒排 BM25；精排挂了退回 RRF 分；重排挂了退回精排顺序；链路允许 2 层同时降级仍返回可用结果。

这一节 takeaway：搜索系统的服务边界不是业务边界，而是漏斗层 + SLA 边界；任一层必须自带 fallback，链路级降级比单点高可用更关键。

## 4. Deep Dives

这一节把漏斗四层 (查询理解 / 检索 / 排序 / 索引维护) 逐一展开，每层给出默认 pick、三到四个候选、逐个 why-not、切换触发条件与常见追问。读完这四个子节，可以把"搜索系统每层算法选型"的工具箱摆清楚、面试官任意单层深挖都不卡壳。编排顺序与在线数据流一致：查询理解在前、检索在中、排序在后、索引维护贯穿全程。

### 4a. Query Understanding (查询理解)

查询理解把用户原始输入转换成结构化检索意图，是搜索系统中投资回报率最高的模块之一——拼写纠错能挽回 5-10% 流量、**Query Rewriting** (查询重写) 能拉升长尾召回 15-20%。pipeline 五阶段：Tokenization → Spell Correction → Query Rewriting → Intent Classification → **Named Entity Recognition** (NER, 命名实体识别)。

分词我选 **Byte Pair Encoding** (BPE, 字节对编码)，因为字节级基元适用多语言 + OOV 鲁棒、与 GPT / BART 等下游模型同源。候选一是 **WordPiece** (BERT 系)——BPE 贪心变种，但中文 subword 切分偏细，WordPiece 更合适的位置是纯英语栈，不用。候选二是 **SentencePiece + Unigram LM**——概率模型表达灵活，但训练慢 2-3×，SentencePiece 更合适的位置是 T5 / mT5 多语场景，淘汰。候选三是 **Jieba 传统中文分词**——纯中文语义单元清晰，但跨语言失效 + OOV 兜底弱，Jieba 更合适的位置是纯中文 NER 前置。切换触发：下游切 T5 / mT5 时迁 SentencePiece；纯中文场景退 Jieba。

**Query Rewriting** 我选 **LLM-based rewriter**，因为 LLM 理解模糊意图强、可生成多样表达 + 指代消解 + 同义词扩展、不需改索引、ROI 最高。候选一是 **Rule-based 同义词注入**——可解释性最强，但长尾扩展不足 + 规则爆炸维护难，Rule-based 更合适的位置是品牌/型号硬性同义 (iPhone 15 ↔ 苹果15)。候选二是 **Pseudo Relevance Feedback** (PRF, 伪相关反馈) BM25 扩展——top-k 高频 term 回填 query，但扩展 term 噪声高 + 对短 query 漂移严重，PRF 更合适的位置是长 query + 专业领域 (学术检索)，淘汰。候选三是 **Seq2seq learned rewriter** (T5 / BART)——训练数据可控，但需 10M+ 标注对 + 冷启慢，Seq2seq 更合适的位置是 LLM 成本不可接受时的替代。切换触发：LLM 调用成本 > 10% serving 预算时迁 Seq2seq；纯品牌搜索退 Rule-based。

意图分类我选 **BERT 分类器**，因为预训练 + 微调 pipeline 成熟、intent ~20-50 类 + 每类 ~10K 样本可冷启、p99 < 10ms。候选一是 **LLM zero-shot** (GPT-3.5 / Claude)——不需标注，但延迟 200-500ms + 成本高 + 稳定性差，LLM zero-shot 更合适的位置是 long-tail intent 离线 label augmentation，淘汰。候选二是 **FastText**——训练推理极快 + CPU-friendly，但语义泛化弱于 BERT + 长尾 intent 准确率低 10-15%，FastText 更合适的位置是千 QPS 以下轻量产品。候选三是 **GBDT**——可解释性强，但特征工程成本高 + 迭代慢，GBDT 更合适的位置是 early-stage 冷启基线，不用。切换触发：schema 频繁变化时迁 LLM zero-shot；QPS < 1K 时退 FastText。

拼写纠错走 **编辑距离 + Language Model** (默认)：计算简单、无需 GPU、覆盖 90%+ 常见错误；BERT-based spell correction 延迟 +30ms 打超预算；SymSpell 对罕见词失效；Noisy Channel Model 训练数据需求大、学术研究级。NER 走 **BERT-CRF** 序列标注默认；BiLSTM-CRF 深度学习早期黄金已淘汰；LLM zero-shot 稳定性不足；Regex + Gazetteer 召回差。整体 query understanding 的 takeaway：五阶段是独立模块、可独立迭代、可独立 A/B，任一阶段挂了链路可 degrade 到上游原始信号，是工业搜索团队最高 ROI 投入方向。

> **常见追问**:
> 1. "拼写纠错触发阈值怎么定？" —— 编辑距离 ≤ 2 + LM 分阈 + zero-result query 必纠；避免纠错过度反而降 recall。
> 2. "多语言 query 怎么处理？" —— 先 language detection (fastText) 路由到对应 pipeline、每语种独立 tokenizer + NER。
> 3. "LLM rewriter 怎么防幻觉？" —— 限制输出 schema + 后置语义 filter (BM25 zero-result 回退原 query) + A/B 监控。

### 4b. Retrieval: Sparse + Dense + Hybrid

检索层是"在 10B 文档里圈出 top-1000"的核心——单独稀疏 recall 不够、单独稠密精确匹配差、**Hybrid Retrieval** (混合检索) 是工业标配。BM25 评分公式：

$$
\text{BM25}(q, d) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{f(t, d) \cdot (k_1 + 1)}{f(t, d) + k_1 \cdot (1 - b + b \cdot \frac{|d|}{\text{avgdl}})}
$$

其中 $f(t,d)$ 是词频，$k_1 \approx 1.2$ 控制词频饱和，$b \approx 0.75$ 控制文档长度归一化，**Inverse Document Frequency** (IDF, 逆文档频率) 衡量词稀有度。

L0 稀疏路我选 **BM25** (默认 Lucene 实现)，因为无需训练 + 精确匹配效果最强 + 参数极少可冷启 + 经 20 年工业验证、对长尾查询远好于稠密。候选一是 **TF-IDF**——更老更简单，但文档长度归一化弱 + 召回 5-10% 低于 BM25，TF-IDF 更合适的位置是无 avgdl 统计的静态小库，淘汰。候选二是 **Boolean Retrieval** (纯 AND/OR)——无打分只过滤，但无法排序 top-K，Boolean 更合适的位置是高级检索的 filter 语法。候选三是 **SPLADE**——学习式稀疏 token 权重、比 BM25 召回 + 5-10%，但训练样本需求大 + 索引写入慢 3×，SPLADE 更合适的位置是 BM25 跑通后的升级。候选四是 **DocT5Query**——离线用 T5 为每文档生成潜在 query，但训练成本大 + 索引体积 +30%，DocT5Query 更合适的位置是文档数 < 1B 场景。切换触发：召回 bottleneck 是精确匹配质量时迁 SPLADE；文档量可控时叠 DocT5Query。

L1 稠密路我选 **Dense Passage Retrieval** (DPR, Bi-Encoder 双塔)，因为 query 塔 / doc 塔独立训练 + 文档 embedding 离线预算、在线只做 query 塔 + ANN、p99 10-20ms、与 HNSW / FAISS 工具链兼容。候选一是 **ColBERT** (Contextualized Late Interaction)——token 独立 embedding + late interaction、精度 + 3-5%，但 index size 扩大 20× + serving 内存爆炸，ColBERT 更合适的位置是文档量 < 10M 的学术/医疗检索。候选二是 **ANCE**——hard negative mining 召回 + 2%，但训练 pipeline 复杂 + 迭代慢，ANCE 更合适的位置是 DPR 跑通后的 recall 优化，保留升级路径。候选三是 **Contriever** (无监督 Bi-Encoder)——不需标注、冷启友好，但 supervised DPR 精度仍高 3-5%，Contriever 更合适的位置是无点击标注起步期，淘汰作主路。候选四是 **BGE / E5** (多语言通用 embedding)——多语言预训练强，但垂直领域微调后仍被领域 DPR 超，BGE 更合适的位置是多语言冷启基线。切换触发：精度极敏感且文档规模 < 10M 时迁 ColBERT；标注不足时从 Contriever 升 DPR 再 ANCE。

**Hybrid Retrieval** 融合我选 **RRF** (倒数排名融合) $\text{RRF}(d) = \sum_{r \in R} \frac{1}{k + r(d)}$，其中 $r(d)$ 是文档在排名 r 中位置、$k \approx 60$ 平滑。因为 RRF 免 score 标定 + 对两路分数尺度不敏感 + 实现 O(K) 简单。候选一是 **Linear Combination** $s = \alpha \cdot s_{\text{BM25}} + (1-\alpha) \cdot s_{\text{dense}}$——直观可解释、$\alpha$ 可调，但 BM25 分与 dense cosine 尺度差 10× + 需校准 + 漂移频繁，Linear Combination 更合适的位置是 offline 调参。候选二是 **Learned Combiner** (小 MLP 或 GBDT)——自动学权重 + 可加 query 特征，但需标注 + 迭代慢，Learned Combiner 更合适的位置是 RRF 跑通后的精排前融合。候选三是 **CombMNZ** (经典 IR 融合)——学术历史方案、多路相加归一化，但不如 RRF 简洁 + 不考虑 rank 信息，CombMNZ 更合适的位置是 90 年代信息检索论文，淘汰。切换触发：有充足标注时迁 Learned Combiner 学 query-dependent 权重。

> **常见追问**:
> 1. "Hybrid gain 从哪来？" —— 稀疏捕获精确 token 匹配 (品牌/型号/专有名词)、稠密捕获语义相似 (近义词/改写查询)，两路互补、NDCG 通常 +5-15%。
> 2. "长尾查询怎么办？" —— 稀疏路兜底 (rare term IDF 极高)、稠密路对长尾泛化强、RRF 融合让短头 + 长尾都受益。
> 3. "zero-shot retrieval 怎么做？" —— 预训练 Contriever / E5 / BGE 直接跑、无需目标领域标注、作为冷启基线、然后用点击日志微调 DPR。

### 4c. Ranking & Re-Ranking

排序层是"在 top-1000 里重排出 top-10"的精细环节——延迟预算 20-30ms、必须引入更多特征交互 + LTR 信号。**LTR** 三范式：

| 范式 | 损失 | 代表算法 |
|------|------|---------|
| **Pointwise** (逐点) | 回归/分类 | Linear Regression, **GBDT** |
| **Pairwise** (逐对) | 比较文档对相对顺序 | **RankNet**, **LambdaRank** |
| **Listwise** (列表级) | 直接优化列表指标 | **LambdaMART**, **ListNet** |

排序质量离线评估用 NDCG:

$$
\text{NDCG@k} = \frac{\text{DCG@k}}{\text{IDCG@k}}, \quad \text{DCG@k} = \sum_{i=1}^{k} \frac{2^{r_i} - 1}{\log_2(i + 1)}
$$

$r_i$ 是位置 i 的相关性等级 (0-4)、**Discounted Cumulative Gain** (DCG, 折损累积增益) 按位置折损求和、**Ideal DCG** (IDCG) 归一化。NDCG 是工业界最常用 ranking 指标；在线指标 (点击率、停留时间、SAT) 在决策中比 NDCG 更重要。

L2 精排我选 **LambdaMART** (LightGBM 实现)，因为 Listwise loss + 梯度提升树、直接优化 NDCG、CPU 一小时跑通 10M 样本、工业界 SOTA 超 10 年。候选一是 **LightGBM pointwise**——同框架 + Pointwise CTR 回归，但不优化排序 + NDCG 低 3-5%，LightGBM pointwise 更合适的位置是冷启或 CTR 校准。候选二是 **RankNet** (深度 pairwise)——早期深度 LTR，但训练对 pair 采样敏感 + 工程复杂度高，RankNet 更合适的位置是历史遗留或纯神经系统，淘汰。候选三是 **Cross-Encoder BERT**——精度 + 3-8%，但延迟 100-200ms 打 20ms 预算爆表 + 需 GPU，Cross-Encoder 更合适的位置是 top-50 二次精排 (L2.5) 而非主 ranker，保留 rerank upgrade。候选四是 **MonoT5**——生成式精度高，但延迟更高 + 部署成本大，MonoT5 更合适的位置是离线 label 生成。切换触发：GPU 预算充足且延迟可放宽到 100ms 时叠 Cross-Encoder 做 L2.5。

Cross-Encoder 重排 (L2.5) 我选 **BERT-base Cross-Encoder** (fine-tuned on click log)，因为 Bi-Encoder 无法捕获 query-doc token-level 语义交互 + top-50 规模 BERT-base 延迟 50-80ms 可接受。候选一是 **MonoT5** (T5-base)——精度 + 2%，但延迟 2-3× BERT + T5 架构慢，MonoT5 更合适的位置是离线 data augmentation。候选二是 **ColBERT late interaction**——token 级交互但 index size 爆炸 (§4b 已述)，ColBERT 更合适的位置是 retrieval 层而非 rerank，淘汰 rerank 主路。候选三是 **RankLLaMA / Cohere Rerank**——LLM 直接打分精度 SOTA，但延迟 300ms+ 成本高 10-20×，LLM rerank 更合适的位置是 SaaS + 低 QPS 场景。候选四是 **BERT-Large**——精度 + 1-2%，但延迟 +50%，BERT-Large 更合适的位置是预算允许场景。BERT-base Cross-Encoder 是 L2.5 最佳起点，三个替代各有 why-not、切换条件清晰。切换触发：预算允许 + 延迟可放宽时上线 RankLLaMA；QPS > 10K 且预算紧时回退 BERT-base。

> **常见追问**:
> 1. "LambdaMART 特征哪里来？" —— BM25 / dense similarity / click-rate / freshness / personalization / 用户-文档历史交互 / domain authority，100-500 维 handcrafted + dense embedding pooling。
> 2. "position bias 怎么处理？" —— 训练时把 position 作为 bias feature (PAL) 或用 Inverse Propensity Scoring (IPS, 逆倾向分) 加权、serving 时置零。
> 3. "离线 NDCG 提升但在线 CTR 不涨？" —— 先查 label quality、再查分布偏移、最后查融合 stage 尺度重标定。

### 4d. Index Management & Freshness

索引维护是搜索系统的基础设施底座——负责 ingest、sharding、replication、incremental update、compaction 与 canary validation。核心矛盾是"新文档可见时延"与"索引 build cost"的 tradeoff。

增量索引策略我选 **双索引架构 (batch + stream)**：主索引日级全量 rebuild、实时 delta 索引每 10 分钟 merge 小 Lucene segment 进 main。因为它兼顾新鲜度 (< 10min 可召回) 与 rebuild 兜底、Lucene 的 NRT API 天然支持。候选一是 **pure batch 日级全量**——rebuild 简单稳定，但新文档 24h 不可见，pure batch 更合适的位置是学术 / 法律文档库 + 低新鲜度需求，不用。候选二是 **pure streaming**——Kafka 流直写 Lucene，但无法 global compaction + segment 碎片化严重 + 无 rebuild 兜底，pure streaming 更合适的位置是小规模 log search (ELK)，淘汰。候选三是 **continuous rebuild** (每 30min 跑一轮)——延迟 30min + cost 极高 + IO 爆炸，continuous rebuild 更合适的位置是 < 100M docs + 硬件预算无限，不用。切换触发：新鲜度 SLA 放宽到 1h+ 时退 pure batch；规模 < 100M 时可 pure streaming。

**Tiered Index** (分层索引) 策略我选 **hot / warm / cold 三层**：hot 层放最近 7 天 + 高频文档 (in-memory)、warm 层 7-90 天 (SSD)、cold 层 90 天+ (S3 按需 rehydrate)。因为流量 80/20 分布让 hot 命中率 > 80% 大幅降成本。候选一是 **flat single-tier all-in-memory**——延迟最低，但 10B × 20TB 全内存成本 10×、经济性差，flat 更合适的位置是 < 100M docs + 成本不敏感。候选二是 **time-based single-tier**——只按时间切、没频率考虑，time-based 更合适的位置是纯时序文档库，淘汰。候选三是 **query-class partitioned tiering**——按 query 类型路由，但 routing 复杂 + 维护难，query-class 更合适的位置是多 vertical 平台 (Yelp)。切换触发：长尾查询占比 > 30% 时扩 cold 层至 SSD。

**Canary Query** (金丝雀查询) 机制：每次新索引上线前，用固定的 1K-10K 历史 query 跑回归测试，NDCG / recall / 响应码分布若偏离 baseline > 5% 则自动 rollback。这是搜索系统避免"无声降级"的必要防线。整体索引机制在 document-partitioned sharding + 3× replication + dual-index (batch + stream) + tiered (hot/warm/cold) + canary gate 五件套组合下稳稳撑起 10B 文档 + 10min 新鲜度 + 零停机升级。

> **常见追问**:
> 1. "索引 merge 怎么防止影响查询？" —— 后台 segment merge 异步进行、查询路径走 readOnlyView、merge 完成后原子切换。
> 2. "Scatter-Gather fan-out 延迟尾部怎么控？" —— backup request (同一 query 发两份取先到) + straggler 检测 + reroute、p99.9 可从 10× 压到 1.5×。
> 3. "Canary query set 怎么维护？" —— 按时间周期重采样 top / tail / zero-result 三段、加权覆盖实际流量分布、避免 stale canary 让 regression 检测失效。

这一节 takeaway：搜索系统不是一个模型、而是四层算法候选池的组合；每层默认方案都得搭配至少 3 个候选 + why-not + 切换条件，才算真正"讲透选型"。

## 5. Reliability (Monitoring & DR, 5m)

搜索系统的可靠性不是"整条链路 100% 不挂"，而是"每一层都有独立 fallback、整体降级到可接受质量"的分层容错。

监控策略我选 **四象限监控 + 分层 SLO**，因为系统 / 模型 / 业务 / 实验四维度独立 + 分层 SLO 让降级决策可编程。系统层对接 **Prometheus** + **Grafana** 采 p99 / error rate；模型层引入 **Evidently** 或 **Arize** 采 BM25 分布漂移、dense embedding 退化；业务层看 SAT、zero-result rate；实验层看分桶平衡 / SRM / novelty。候选一是 **Datadog 单栈**——工具链统一但模型漂移细节看不出，Datadog 更合适的位置是中小团队省运维，不用。候选二是 **Arize 独立 ML 监控**——ML 指标全，但与系统监控割裂 + 告警双头，Arize 独立栈更合适的位置是 MLE 独立团队，淘汰。候选三是 **Fiddler**——可解释性专精，但 Prometheus 整合成本高 + 许可证贵，Fiddler 更合适的位置是金融 / 医疗强合规。候选四是 **自建 full-stack**——灵活度高但研发成本大，自建更合适的位置是 FAANG 规模深度定制。切换触发：模型漂移成为故障主源时叠 Arize。

降级预案分层：查询理解挂了退回 raw query + 基础 tokenization；稠密路挂了退回纯 BM25；Ranker 挂了退回 RRF 分序；Re-Rank 挂了返回 Ranker 原始顺序；特征缺失用 per-feature default (7 天滑动均值) 兜底；索引 primary shard 挂了 fallback 到 replica。每条 fallback 路径必须独立演练、月度 game day 跑一次。SLO 清单：(a) 系统 SLO p99 端到端延迟 < 100ms + 月度 unavailability < 22 分钟；(b) 模型 SLO 离线 NDCG@10 ≥ 基线 0.75 + 在线 click@1 ≥ 40%；(c) 业务 SLO zero-result rate < 2% + SAT rate ≥ 65%；(d) 成本 SLO 单 query 成本 < $0.0001 不含广告。

这一节 takeaway：reliability 不在单点高可用而在分层可降级，四象限监控 + 每层独立 fallback + canary query 是搜索系统高可用的必选项。

## 6. Summary & Tradeoffs

本题核心 takeaway 是搜索系统的分层思维：查询理解 / 检索 / 排序 / 索引维护四层各有独立候选池，每层选型伴随 Pick + 3-4 候选 + why-not + 切换条件五元组。检索默认 BM25 + DPR 混合 + RRF、排序默认 LambdaMART + BERT Cross-Encoder 二阶、索引默认 document-partitioned + HNSW/IVF-PQ + dual-index (batch + stream)。

三个最常被错答的 tradeoff：一是稀疏能否被稠密完全替代——不能，因为稀疏捕获精确 token 匹配 + 对长尾 rare term 远好于稠密，混合检索才是工业标配；二是 LLM re-rank 是否马上上线——不是，因为 LLM 延迟 300ms+ 打端到端 100ms 预算爆表，LLM 留给低 QPS 场景；三是 Real-time indexing 是否应覆盖全库——不是，因为双索引 (batch + stream) 在新鲜度与 rebuild cost 间取平衡，pure streaming 在 10B 规模下 segment 碎片化无法运维。

工程 vs 建模决策的主要拉锯在两处：一是 ANN 索引在 HNSW 与 IVF-PQ 之间取舍，recall 优先 HNSW + 规模 ≤ 1B、规模 10B+ 成本敏感时倾向 IVF-PQ；二是 Ranker 在 LambdaMART 与 Cross-Encoder 之间取舍，延迟优先 LambdaMART、延迟可放宽则叠 BERT Cross-Encoder 做 L2.5。真正判据不是谁更先进，而是业务的文档规模、QPS、延迟预算、成本敏感度落在哪个拐点。

## Interview Q&A

下面三个问题是本题高频被追问的边界题，每个都有典型陷阱。

第一题："长尾查询 (占 30% 流量但 zero-result rate 高) 怎么办？"——典型 recall vs precision 失衡。答案思路：(a) 查询理解侧强化拼写纠错 + 同义词扩展 + LLM 查询重写；(b) 检索侧强化稠密路 (对语义泛化比 BM25 强 5-10%) + 补 SPLADE 学习式稀疏；(c) 排序侧加 query difficulty 特征让 ranker 对长尾更保守；(d) 业务侧 "did you mean" + 相关搜索 + related entity 卡片拉回意图；(e) 监控 zero-result rate 作为核心 SLO。

第二题："zero-shot retrieval (无点击标注) 怎么设计？"——冷启类典型题。答案思路：(a) 通用 embedding (Contriever / E5 / BGE multilingual) 做 dense baseline；(b) BM25 作稀疏兜底 + RRF 融合 (两路都不需训练)；(c) 上线后收集 click + skip + dwell 弱监督信号、通过 MarginMSE / SimLM 蒸馏迁移；(d) query rewriting 补长尾、query expansion 补同义；(e) query-doc 共现矩阵启动 co-click 图做 bootstrap 训练数据。整体 zero-shot → 弱监督 → supervised 的数据飞轮是关键。

第三题："增量索引与 compaction 怎么做？"——索引维护类典型题。答案思路：(a) 双索引架构 (主索引日级全量 rebuild + delta 索引每 10min merge)；(b) delta 索引基于 Lucene NRT API、查询时 union main + delta、segments 过 100 时强制 merge；(c) compaction 后台异步、查询路径走 readOnlyView、原子切换避免抖动；(d) 每次索引上线前跑 canary query set (1K-10K 历史 query) 做 NDCG / recall 回归、偏离 baseline > 5% 自动 rollback；(e) cold tier 按月归档到 S3 + 按需 rehydrate、避免长尾占 hot 内存。目标是 freshness < 10min + rebuild cost 可控 + 零停机。

## Self-Check

自检清单：离开白板前，对着下面八个问题能不看稿答对吗？(1) 多阶段漏斗 L0/L1/L2 每层的延迟预算与目标指标；(2) 每层默认模型与 3-4 个候选 + why-not (查询理解 / retrieval / ranker / rerank)；(3) BM25 公式 + NDCG 公式能否写出；(4) BM25 稀疏 vs Bi-Encoder 稠密 vs ColBERT late-interaction 的延迟 / 精度 / 索引大小 tradeoff 曲线；(5) HNSW / IVF-PQ / ScaNN / Milvus 的内存 vs 精度 tradeoff 在什么文档规模下切换；(6) LambdaMART 为什么是 Listwise + 为何至今 SOTA、与 BERT Cross-Encoder 何时叠加；(7) 双索引架构 (batch + stream) vs pure streaming vs pure batch 的切换条件；(8) 四象限监控 + 每层 fallback + canary query 的降级预案。八个都能答对就可以去白板了。
