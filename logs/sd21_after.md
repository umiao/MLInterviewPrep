=== ARCHITECTURE (7770 chars) ===
## 高层架构 (High-Level Architecture)

### 组件总览 (Component Overview)

系统分为**上传/处理管道 (Upload Pipeline)**和**播放/分发管道 (Playback Pipeline)**
两条主要路径，加上横切的**元数据服务 (Metadata Service)**和**搜索/推荐服务**。

```
[Client] --> [API Gateway / Load Balancer]
                 |
        +--------+--------+
        |                 |
  [Upload Service]   [Playback Service]
        |                 |
  [Object Storage]   [CDN Edge Nodes]
  (S3 / GCS)        (CloudFront/Akamai)
        |                 |
  [Transcoding       [Origin Storage]
   Pipeline]          (S3 / GCS)
   (DAG Worker)
        |
  [Metadata Service] <--> [Video DB (MySQL/PostgreSQL)]
        |
  [Search Service]   [Recommendation Service]
  (Elasticsearch)    (ML Pipeline)
        |
  [View Count Service] --> [Redis] --> [Cassandra]
```

### 核心服务及职责 (Core Services)

#### 1. Upload Service (上传服务)

- 接收客户端通过 **tus 协议** 或 **GCS Resumable Upload** 上传的视频文件
- 大文件 (> 256 MB) 使用**分片上传 (Multipart Upload)**:
  将文件分为 5-25 MB 的块 (chunk)，支持断点续传
- 上传完成后向 **Message Queue (消息队列, 如 Kafka/SQS)** 发送转码任务
- 同时提取视频基础元数据 (时长、分辨率、编码格式、文件大小)
- **分块上传机制 (Chunked Upload Mechanics)**: 客户端以 **resumable chunked upload** 模式将原始视频切成 **10-50 MB 的块 (chunk)**, 通过 HTTPS 直传到**边缘接入服务器 (Edge Upload Server)**, 由边缘服务器异步落盘到 **GCS (Google Cloud Storage) / Colossus** blob 存储. 每个 chunked 段完成后投递一条 **Pub/Sub** 消息 (topic: `video-ingest`), 下游**无状态 FFmpeg Worker 池 (stateless FFmpeg workers)** 在数千实例上并发拉取任务. Worker 无状态, 崩溃后消息重投到其它实例 retry, 已完成的 chunk 不会被重复转码 (每 chunk idempotent)
- **Pub/Sub 优势** (对比 Kafka): 在 GCP 生态内天然多区域广播, 无需管理 partition / ISR, 按消息计费, 适合突发上传峰值 (晚高峰 up to 10x 日均). Kafka 在 on-prem 或成本敏感场景仍是选择

#### 2. Transcoding Pipeline (转码管道)

- **DAG (Directed Acyclic Graph，有向无环图) 工作流引擎**
  (如 Apache Airflow / Temporal / AWS Step Functions)
- 转码流程:
  1. **视频分段 (Video Splitting)**: 将原始视频按 GOP (Group of Pictures) 边界
     分为 4-10 秒的片段，实现并行转码
  2. **并行转码 (Parallel Transcoding)**: 每个片段独立转码为目标分辨率 + 编码组合
     (如 1080p H.264, 720p H.265, 4K AV1)，使用 **FFmpeg** Worker 集群
  3. **片段合并 (Segment Merge)**: 转码后的片段合并为完整视频文件
  4. **缩略图生成 (Thumbnail Generation)**: 从视频中提取关键帧作为缩略图
  5. **内容审核 (Content Moderation)**: 调用 ML 模型检测暴力、色情等违规内容
  6. **版权检测 (Copyright Detection)**: 音频指纹 + 视频指纹与版权数据库比对
     (类似 YouTube **Content ID**)
- **输出**: 多分辨率 + 多编码格式的 **HLS (HTTP Live Streaming)** manifest 文件
  (.m3u8) 和 TS/fMP4 片段文件
- **转码层级政策 (Transcoding Tier Policy)** -- 头部激进, 长尾保守 (cost amortization):
  - **H.264 for all**: 每个视频都必须生成 H.264 版本 (~100% 客户端 兼容), 是兜底保障. 成本最低, 压缩率最差
  - **VP9 for hot**: 热门内容 (前 ~20% 播放量) 额外生成 VP9, 比 H.264 节省 30-40% 带宽. 移动端原生支持
  - **AV1 for head + 4K/8K**: 仅 TOP ~1% 头部 + 所有 4K / 8K 视频 生成 AV1, 比 H.264 节省 50-60% 带宽. AV1 编码成本约 H.264 的 50-100x, 但头部视频播放量集中 (前 1% 视频占总播放 50%+), 对头部内容 bandwidth 节省摊销 ROI 极高; 长尾视频播放量稀疏, 强行 AV1 编码成本收不回来. 原则: **长尾保守头部激进**
- **编码阶梯 (Encoding Ladder)** -- 每分辨率多码率档位:
  - 九级分辨率金字塔: **144p / 240p / 360p / 480p / 720p / 1080p / 1440p / 2160p (4K) / 4320p (8K)**
  - 每档内部再分多码率: 以 **720p** 为例, 同时提供 **1.5 Mbps** (低质), **2.5 Mbps** (中质), **4 Mbps** (高质) 三档; 客户端 ABR 在同分辨率多码率间平滑切换, 避免单次跳分辨率 的视觉突变
  - 阶梯越密用户 QoE 越平滑, 但转码成本线性增长. 实际部署: 每分辨率 2-3 档, 全金字塔总计 ~20 种 rendition (resolution x codec x bitrate 的组合)
- **专用转码 ASIC (VCU / Argos)**: Google 自研**视频编码单元 (Video Coding Unit, VCU, 内部代号 Argos)** ASIC 用于 VP9 / AV1 大规模编码. 相比通用 GPU (NVENC), VCU 在同等功耗下吞吐提升 **7-20x**, 每瓦性能提升 **20-33x**. YouTube 规模下 VCU 约 2 年 摊销回本, 是支撑 AV1 全量推广的硬件基础 (纯 GPU 集群吞吐量不够, 单位功耗成本也不够低). 参考文献: Ranganathan et al., *Warehouse-scale video acceleration* (ASPLOS 2021, VCU/Argos paper)

#### 3. Video Storage (视频存储)

- **原始视频**: 对象存储 (S3/GCS)，存储类型 Standard (热存储)
- **转码后视频**: 对象存储，按访问频率分层:
  - 热门视频 (前 20%): Standard 存储 + CDN 缓存
  - 长尾视频 (80%): **Infrequent Access (IA)** 或 **Glacier** 冷存储
- 存储优化: 对于长尾视频只保留 480p 和 720p 两种分辨率，
  高分辨率版本在请求时动态转码 (**Just-in-Time Transcoding**)
- **存储分层 (Storage & Metadata Split)** -- 不同数据类型选不同底座:
  - **Blob (视频二进制 + 所有 rendition)**: **Colossus** (Google 下一代分布式文件系统, GFS 继任者, GCS 是其上层封装). 采用 Reed-Solomon 纠删码 (典型 6,3): 空间利用率 ~67% (相比 3x 副本的 33%) 但容错能力相当, PB 级规模下每年节省数亿美金存储成本
  - **结构化元数据 (视频 metadata / rendition 索引 / 播放位点 / 轻量用户画像字段)**: **Bigtable** (稀疏列宽行, 行键自动分片). 单表容纳 10 亿+ 视频元数据, 行键 `video_id` 使请求均匀分布, 无需手工分片. Bigtable 的定位: 无 JOIN, 无事务, 但线性扩展到 PB 级容量与百万 QPS, 是 YouTube / GCS / Google Search / Maps 共用的 NoSQL 底座
  - **全文搜索 (标题 / 描述 / 字幕 OCR / ASR 转写)**: **Elasticsearch** (倒排索引 + BM25 + 向量 ANN 混合 retrieval)
  - **版权指纹库 (Content ID fingerprint)**: 音频 **Chromaprint** 128-bit + 视频 **pHash** 60-bit 双通道比对, 存在独立 **Bigtable** 表 (按指纹哈希分片), 上传完成后触发异步匹配 + 命中即进入版权申诉 流程. 这是 YouTube 与其它 UGC 平台在法律/合规上的核心护城河

#### 4. CDN & Playback Service (CDN 与播放服务)

- **CDN 多层缓存架构**:
  - L1: 边缘 POP (Point of Presence) -- 全球 200+ 节点，缓存热门视频片段
  - L2: 区域 Shield (区域保护层) -- 每个大区 (北美、欧洲、亚太) 1-3 个节点，
    减少回源请求
  - L3: Origin (源站) -- S3/GCS 对象存储
  - **Google Global Cache (GGC) / ISP 嵌入层**: 除自建 POP 外, 还将缓存节点**直接部署到 ISP 机房的 rack 内** (与 Netflix **Open Connect Appliance** 同构). 用户流量不出 ISP 即可拿到视频, RTT 降到 **< 5 ms**, 回源流量减少 **70%+**, 大幅降低 ISP 之间 的跨网结算成本 (settlement-free peering). GGC 形成 `ISP rack -> 区域 Shield -> Origin (Colossus)` 三层 CDN 架构, 是 YouTube / Netflix 这种巨头内容方能进入 ISP 骨干的关键杠杆
- **ABR (Adaptive Bitrate) 播放流程**:
  1. 客户端请求 manifest 文件 (.m3u8 / .mpd)
  2. manifest 包含所有可用分辨率的片段列表和带宽要求
  3. 播放器根据当前网络带宽和缓冲区状态选择最优分辨率
  4. 网络波动时自动降级 (如 1080p -> 720p -> 480p)
- **协议选择**:
  - **HLS (HTTP Live Streaming)**: Apple 生态首选，最广泛支持
  - **DASH (Dynamic Adaptive Streaming over HTTP)**: 开放标准，Android/Web 首选
  - 实际部署: 同时生成 HLS + DASH manifest，客户端按能力选择

#### 5. Metadata Service (元数据服务)

- 存储视频元数据: 标题、描述、标签、上传者、时长、分辨率列表、
  缩略图 URL、上传时间、审核状态
- **数据库选择**: **MySQL** (主库, 写入) + **Read Replicas** (读取)
  - 视频元数据表: ~50 字段, 行数 = 视频总数 (~10 亿)
  - 索引: video_id (主键), uploader_id, upload_time, category
- **缓存**: **Redis** 缓存热门视频元数据，TTL 5 分钟，命中率 > 95%

#### 6. View Count Service (观看计数服务)

- **写入路径**: 播放事件 -> Kafka -> 聚合 Worker -> Redis (实时计数) -> Cassandra (持久化)
- **近实时更新**: Redis 中的计数每 30 秒批量刷新到 Cassandra
- **反刷量 (Anti-fraud)**: 相同 user_id + video_id 在 24 小时内只计一次有效观看;
  使用 **HyperLogLog** 估算独立观看者数 (UV)
- **设计权衡**: 牺牲实时精确性换取高吞吐量。精确计数在 T+1 通过批处理校准

#### 7. Content-to-Feature Bridge (内容 -> 特征桥)

**多模态管道 (Multimodal Pipeline)** 在转码完成后异步触发, 对原始视频并行抽取:

- **视频帧 embedding (Video-BERT-like)**: 每 2 秒采样一帧, 经 VideoMAE / Video-BERT / VJEPA 生成 ~512-dim embedding, 用于 "视觉相似内容" 召回
- **ASR (Automatic Speech Recognition, 自动语音识别)**: Whisper / USM 将音轨转字幕, 同时产出时间对齐的文本 token 序列 (支撑多语字幕 + 全文检索)
- **OCR (Optical Character Recognition, 光学字符识别)**: 对关键帧 识别嵌入字幕 / 贴纸 / 标牌 / 横幅文本
- **音频指纹 (Content ID fingerprint)**: Chromaprint 用于版权检测 + 音乐识别
- **Topic classification**: 多标签分类器输出 ~1000 细粒度 topic (用于分区运营与冷启 taxonomy)
- **Thumbnail scoring**: CTR 预估模型对候选封面帧打分, 选最优 缩略图

这些多模态特征**同时**喂给两条下游链路:

1. **搜索索引** (Elasticsearch 文本字段 + 向量字段): 实现从 "标题/描述" 浅层检索扩展到 "视频内容语义" 深层检索
2. **推荐系统 retrieval / ranking** (见 framework node id=198 Real-Time Recommendation): 实现基于内容语义的**冷启召回** (新视频没有交互信号时靠 embedding 相似找受众) 和 **相关性排序** (ranker feature 里 content embedding 与 user embedding 的交互)

**关键设计点**: 同一份多模态管道为搜索 + 推荐两条业务链路共享, 避免重复抽取 (frame embedding 单次 ~GPU-秒级, 重复抽取成本 不可接受). 这是内容平台 (YouTube / Netflix / TikTok / 小红书) 的标准架构模式 -- 内容理解层是一个 platform capability, 不是 per-vertical 的工具.

#### 数据库选择与理由 (Database Choices)

| 数据类型 | 数据库 | 理由 |
|---------|--------|------|
| 视频元数据 | MySQL + Read Replicas | 结构化数据, 需要事务和关联查询, 读多写少 (100:1) |
| 观看计数 | Redis + Cassandra | 超高写入吞吐 (百万级 QPS), 最终一致即可 |
| 搜索索引 | Elasticsearch | 全文搜索 + 模糊匹配 + 相关性排序 |
| 用户行为日志 | Kafka + S3 (Parquet) | 流式摄入 + 批量分析, 保留原始数据用于 ML 训练 |
| 视频文件 | S3 / GCS | 对象存储, 11 个 9 的持久性, 按访问分层 |
| 推荐模型特征 | Redis (Feature Store) | 低延迟特征读取 (P99 < 5ms) |

### 通信模式 (Communication Patterns)

- **同步 (REST/gRPC)**: 客户端 <-> API Gateway, Metadata 查询, 搜索请求
- **异步 (Kafka)**: 上传完成 -> 转码任务, 播放事件 -> 计数聚合, 用户行为 -> 推荐
- **WebSocket**: 视频处理状态实时推送 (转码进度、审核结果)


=== TRADEOFFS (2523 chars) ===
## 权衡讨论 (Trade-off Discussion)

### 关键设计决策 (Key Design Decisions)

| 决策 | 选项 A | 选项 B | 我们的选择与理由 |
|------|--------|--------|----------------|
| 转码策略 | 预转码所有分辨率 (Eager) | 按需转码 (JIT) | **混合**: 热门创作者预转码全分辨率; 长尾视频仅预转码 480p+720p, 其余 JIT。节省 60% 存储成本 |
| CDN 架构 | 单一 CDN | 多 CDN | **多 CDN**: Primary (CloudFront) + Fallback (Akamai)。单 CDN 故障影响全球; 多 CDN 增加成本 15% 但消除单点故障 |
| 视频编码 | H.264 (兼容性最好) | AV1 (压缩率最高) | **渐进迁移**: 新内容同时提供 H.264 + AV1; AV1 压缩率比 H.264 好 30-50%, 但编码速度慢 10x, 需要 GPU。2-3 年内逐步淘汰 H.264 |
| 分段协议 | HLS 6-10 s 段 | DASH 1-5 s 段 | **同时生成**: iOS/Apple 端必须 HLS (原生支持); Android/Web 优先 DASH (开放标准). DASH 短段在移动网络下**减少 rebuffering 最多 30%** (启动和切换粒度更细), 代价是 manifest 请求频率高 2x, CDN 命中率略低; 短段也允许 low-latency DASH (LL-DASH) 把直播 端到端延迟压到 ~3 s |
| 元数据存储 | 单一 MySQL | MySQL + Redis + ES | **多存储**: MySQL (事务源), Redis (热缓存), ES (搜索)。复杂度高但各取所长 |
| 观看计数 | 精确实时 | 近似 + 批量校准 | **近似 + T+1 校准**: 实时精确计数在 10M QPS 下成本过高; 近似足够用于排序和展示; 创作者收益 T+1 精确结算 |

### 一致性 vs 可用性 (CAP 定理应用)

**视频播放 (AP, 选择可用性)**:
- 即使元数据有几秒延迟 (如刚上传的视频标题更新)，也要保证播放不中断
- CDN 缓存天然是最终一致的: 旧版本 manifest 可能被缓存最多 5 分钟
- 观看计数在不同区域可能短暂不一致 (相差几千次)，用户可接受

**视频上传元数据 (CP, 选择一致性)**:
- 上传完成后，创作者必须立即看到自己的视频状态 (强一致读取)
- 使用 **Read-After-Write Consistency**: 创作者的请求路由到 MySQL 主库
- 其他用户看到该视频可以有几秒延迟 (异步复制到 Read Replica)

### 成本 vs 性能权衡

| 方案 | 月成本 | TTFB P99 | 存储效率 |
|------|--------|---------|---------|
| 全预转码 + 单 CDN | $60M | 200ms | 低 (2 EB 全热存) |
| 全预转码 + 多 CDN | $70M | 150ms | 低 |
| **混合转码 + 多 CDN** | **$80M** | **200ms** | **高 (600 PB 混合存储)** |
| 全 JIT + 多 CDN | $50M | 800ms (首次) | 最高 |

我们选择混合转码 + 多 CDN: 平衡了成本和用户体验。JIT 首次访问延迟太高;
全预转码存储成本不可接受。

### 复杂度 vs 简洁度

**复杂点: 多层缓存架构**

CDN L1 -> CDN L2 Shield -> Origin 的三层缓存增加了运维复杂度:
- 缓存失效需要在三层同步 (视频下架/版权移除)
- 调试播放问题时需要追踪请求经过了哪些节点
- 不同层的 TTL 设置相互影响

**缓解措施**:
- **统一缓存失效 API**: 一个 API 调用触发所有层的 purge
- **请求追踪**: 每个请求携带 X-Request-ID，CDN 和 Origin 都记录，
  用 **Jaeger** 做分布式追踪
- **缓存 TTL 策略文档化**: manifest 文件 TTL 60s, 视频片段 TTL 24h,
  缩略图 TTL 7d

### 10x / 100x 规模变化

**10x (100 亿 DAU, 500 亿日播放)**:
- CDN 带宽从 700 Gbps 增长到 7 Tbps, 需要自建 CDN 节点
  (参考 Netflix **Open Connect Appliance**)
- 转码集群从 3,000 GPU 扩展到 30,000 GPU, 考虑使用
  **Spot Instances** 降低成本 (可容忍转码延迟增加)
- MySQL 元数据库分片 (按 video_id hash 分 16 个 shard)
- S3 存储成本成为最大项, 引入自研对象存储或
  **Ceph** (参考 Bilibili 的实践)

**100x (1000 亿 DAU, 5000 亿日播放)**:
- 需要**自建骨干网络 (Private Backbone)** 连接自建 CDN 节点
  (参考 Google B4 网络)
- 存储层从对象存储迁移到**分布式文件系统** (如 HDFS 变体)
- 转码使用**专用 ASIC** (如 Google Argos) 替代通用 GPU
- 推荐系统从批量更新改为**在线学习 (Online Learning)**,
  实时特征更新
- 月成本从 $80M 增长到 ~$3B (非线性, 因为自建基础设施有规模效应)

