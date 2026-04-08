"""Populate interview-video-streaming system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design YouTube/Netflix
Video Streaming -- upload + transcoding pipeline, adaptive bitrate streaming
(HLS/DASH), CDN edge caching, metadata service, view counting, and copyright
detection.
Idempotent: creates record if missing, overwrites existing.

Chinese translation with English technical terms preserved (bold + first-use
explanation). Formulas and code blocks kept as-is.
"""
import re
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work when run as a script
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

SLUG = "interview-video-streaming"
TITLE = "Design YouTube/Netflix Video Streaming"
DISPLAY_ORDER = 112

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个**视频流媒体平台 (Video Streaming Platform)**，类似 YouTube 或 Netflix，
支持视频上传、转码、存储、分发和播放。系统需要处理海量视频内容的上传与处理，
并通过 **CDN (Content Delivery Network，内容分发网络)** 向全球用户提供低延迟、
高质量的视频播放体验。

视频流媒体是互联网流量最大的应用类别，占全球互联网流量的 60% 以上。核心挑战
在于：(1) 视频文件体积大，上传和处理耗时，(2) 用户分布全球，需要就近分发，
(3) 不同设备和网络条件需要自适应码率，(4) 版权保护和内容审核是法律要求。

### 功能性需求 (Functional Requirements)

1. **视频上传 (Video Upload)**: 创作者上传视频文件 (支持 MP4, MOV, AVI 等格式)，
   最大 50 GB，支持断点续传 (resumable upload)
2. **视频转码 (Video Transcoding)**: 将原始视频自动转码为多种分辨率
   (240p, 360p, 480p, 720p, 1080p, 4K) 和多种编码格式 (H.264, H.265/HEVC, VP9, AV1)
3. **视频播放 (Video Playback)**: 用户通过 Web/Mobile/Smart TV 观看视频，
   支持 **ABR (Adaptive Bitrate，自适应码率)** 根据网络状况自动切换清晰度
4. **视频搜索与推荐 (Search & Recommendation)**: 基于标题、标签、描述搜索；
   基于观看历史的个性化推荐
5. **社交互动 (Social Features)**: 点赞、评论、订阅、分享

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**: 99.99% -- 视频播放是核心用户体验，
  任何中断都会导致用户流失
- **延迟 (Latency)**: 视频播放启动时间 (Time to First Byte) < 200ms；
  搜索 API P99 < 100ms
- **吞吐量 (Throughput)**: 同时在线观看 5000 万用户；每天 50 万新视频上传
- **持久性 (Durability)**: 视频内容零丢失 (11 个 9 的持久性)
- **可扩展性 (Scalability)**: 每日 10 亿视频播放量 (1B views/day)
- **一致性 (Consistency)**: 视频元数据强一致；观看计数和推荐数据最终一致

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 平台是 UGC (用户生成内容) 还是专业内容 (如 Netflix)?**
   -- WHY: UGC 需要内容审核管道和版权检测 (如 YouTube Content ID)；
   专业内容更关注 DRM (Digital Rights Management) 和独家授权

2. **Q: 是否需要支持直播 (Live Streaming)?**
   -- WHY: 直播需要完全不同的管道 (RTMP 推流 -> 实时转码 -> HLS/DASH 分发)，
   延迟要求从秒级降到亚秒级，架构差异很大

3. **Q: 目标用户分布在哪些地区? 是全球还是特定市场?**
   -- WHY: 决定 CDN 节点部署策略。全球分发需要 50+ 边缘 POP (Point of Presence)；
   单一市场只需 5-10 个

4. **Q: 视频的平均时长和分辨率是多少?**
   -- WHY: 影响存储和转码容量规划。YouTube 平均 7 分钟 720p vs Netflix 平均
   45 分钟 4K，存储和带宽需求差异 10 倍以上

5. **Q: 是否需要离线下载功能?**
   -- WHY: 离线下载需要 DRM 加密打包和设备端解密，增加客户端和存储复杂度

6. **Q: 广告模式还是订阅模式? 还是两者兼有?**
   -- WHY: 广告模式需要广告插入点 (ad insertion points) 和实时竞价系统；
   订阅模式需要付费墙和账号共享控制

7. **Q: 视频观看计数的精确度要求是什么?**
   -- WHY: 如果计数影响创作者收益 (如 YouTube 的广告分成)，需要精确计数和
   反作弊机制；如果仅用于排序，近似计数 (HyperLogLog) 即可

### 范围界定 (Out of Scope)

- 直播流 (Live Streaming) -- 属于独立系统设计题目
- 广告竞价系统 -- 可作为独立模块讨论
- 视频编辑器 / 创作工具
- 付费墙和订阅管理
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 高层架构 (High-Level Architecture)

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

#### 3. Video Storage (视频存储)

- **原始视频**: 对象存储 (S3/GCS)，存储类型 Standard (热存储)
- **转码后视频**: 对象存储，按访问频率分层:
  - 热门视频 (前 20%): Standard 存储 + CDN 缓存
  - 长尾视频 (80%): **Infrequent Access (IA)** 或 **Glacier** 冷存储
- 存储优化: 对于长尾视频只保留 480p 和 720p 两种分辨率，
  高分辨率版本在请求时动态转码 (**Just-in-Time Transcoding**)

#### 4. CDN & Playback Service (CDN 与播放服务)

- **CDN 多层缓存架构**:
  - L1: 边缘 POP (Point of Presence) -- 全球 200+ 节点，缓存热门视频片段
  - L2: 区域 Shield (区域保护层) -- 每个大区 (北美、欧洲、亚太) 1-3 个节点，
    减少回源请求
  - L3: Origin (源站) -- S3/GCS 对象存储
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
"""

# ---------------------------------------------------------------------------
# S3: API Design + Data Flow
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### REST API 端点 (REST API Endpoints)

#### 视频上传

```
POST /api/v1/videos/upload/init
Request: { "filename": "cat.mp4", "size_bytes": 524288000, "content_type": "video/mp4" }
Response: { "upload_id": "up_abc123", "upload_url": "https://storage.example.com/upload/up_abc123",
            "chunk_size": 10485760, "total_chunks": 50 }
Status: 201 Created

PUT /api/v1/videos/upload/{upload_id}/chunk/{chunk_index}
Request: [binary chunk data]
Response: { "chunk_index": 3, "status": "received", "checksum": "sha256:..." }
Status: 200 OK

POST /api/v1/videos/upload/{upload_id}/complete
Request: { "title": "Cute Cat Video", "description": "...", "tags": ["cat","funny"] }
Response: { "video_id": "vid_xyz789", "status": "processing", "estimated_time_sec": 300 }
Status: 202 Accepted
```

#### 视频播放

```
GET /api/v1/videos/{video_id}/manifest
Response: { "hls_url": "https://cdn.example.com/vid_xyz789/master.m3u8",
            "dash_url": "https://cdn.example.com/vid_xyz789/manifest.mpd",
            "available_qualities": ["240p","360p","480p","720p","1080p","4K"],
            "duration_sec": 420, "thumbnail_url": "..." }
Status: 200 OK

POST /api/v1/videos/{video_id}/view
Request: { "user_id": "u_123", "device_type": "mobile", "watch_duration_sec": 120 }
Response: { "counted": true }
Status: 200 OK
```

#### 视频搜索

```
GET /api/v1/search?q=cat+video&page=1&size=20&sort=relevance
Response: { "results": [ { "video_id": "...", "title": "...", "thumbnail": "...",
            "views": 1234567, "duration": "7:23", "uploader": "..." } ],
            "total": 5000, "page": 1, "has_more": true }
Status: 200 OK
```

### 核心数据模型 (Core Data Models)

```sql
-- 视频表
CREATE TABLE videos (
    video_id        VARCHAR(20) PRIMARY KEY,   -- "vid_" + nanoid
    uploader_id     VARCHAR(20) NOT NULL,
    title           VARCHAR(500) NOT NULL,
    description     TEXT,
    duration_sec    INT,
    original_format VARCHAR(10),               -- "mp4", "mov", "avi"
    status          ENUM('uploading','processing','ready','failed','removed'),
    upload_time     DATETIME NOT NULL,
    publish_time    DATETIME,
    view_count      BIGINT DEFAULT 0,          -- denormalized, async updated
    like_count      BIGINT DEFAULT 0,
    category        VARCHAR(50),
    INDEX idx_uploader (uploader_id),
    INDEX idx_upload_time (upload_time),
    INDEX idx_category_views (category, view_count DESC)
);

-- 转码产物表
CREATE TABLE video_renditions (
    rendition_id    VARCHAR(20) PRIMARY KEY,
    video_id        VARCHAR(20) NOT NULL,
    resolution      VARCHAR(10),               -- "720p", "1080p", "4K"
    codec           VARCHAR(10),               -- "h264", "h265", "vp9", "av1"
    bitrate_kbps    INT,
    file_size_bytes BIGINT,
    manifest_url    VARCHAR(500),              -- HLS .m3u8 path
    storage_tier    ENUM('hot','warm','cold'),
    FOREIGN KEY (video_id) REFERENCES videos(video_id)
);

-- 观看事件表 (Cassandra, 宽列存储)
-- PRIMARY KEY ((video_id), event_time, user_id)
-- TTL: 90 days
```

### 读取路径: 视频播放 (Read Path)

1. 客户端请求 `GET /videos/{video_id}/manifest`
2. API Gateway 路由到 **Playback Service**
3. Playback Service 查询 **Redis** 获取视频元数据 (缓存命中率 > 95%)
4. 若缓存未命中，查询 **MySQL Read Replica**，结果写入 Redis (TTL 5 min)
5. 返回 manifest URL (指向 CDN 域名)
6. 客户端请求 CDN 上的 `.m3u8` manifest 文件
7. CDN L1 边缘节点检查缓存:
   - 命中: 直接返回 manifest (延迟 < 20ms)
   - 未命中: 回源到 L2 Shield -> L3 Origin (S3)
8. 客户端解析 manifest，根据当前带宽选择分辨率
9. 客户端逐片段 (segment) 请求视频数据，每个片段 2-10 秒
10. CDN 边缘节点缓存热门片段，命中率 > 90%

### 写入路径: 视频上传 + 转码 (Write Path)

1. 客户端调用 `POST /upload/init` 获取上传 URL 和 upload_id
2. 客户端将文件分为 10 MB 块，逐块上传到 **Object Storage** (直接上传，
   不经过 API Server，使用 **Presigned URL**)
3. 每块上传成功后，Upload Service 记录进度
4. 客户端调用 `POST /upload/{upload_id}/complete`
5. Upload Service 写入视频元数据到 **MySQL** (status = "processing")
6. Upload Service 发送消息到 **Kafka** (topic: video-processing)
7. **Transcoding Pipeline** (Temporal Workflow) 消费消息:
   a. 下载原始视频到本地 SSD
   b. **FFprobe** 检测视频参数 (编码、帧率、分辨率)
   c. 按 GOP 边界分段 (每段 4 秒)
   d. 对每个段并行转码为 N 种分辨率 x M 种编码格式
   e. 合并转码片段，生成 HLS/DASH manifest
   f. 上传转码产物到 S3
   g. 异步触发: 缩略图提取、内容审核、版权检测
8. 转码完成后更新 MySQL (status = "ready")，通过 WebSocket 通知创作者

### 异步路径 (Async Paths)

- **推荐系统**: 用户观看行为 -> Kafka -> Spark/Flink -> Feature Store (Redis) ->
  推荐模型 (每小时更新用户画像)
- **搜索索引**: 视频元数据变更 -> **CDC (Change Data Capture)** -> Elasticsearch
  (近实时索引更新，延迟 < 5 秒)
- **分析管道**: 播放事件 -> Kafka -> S3 (Parquet) -> Spark (每日批量分析)
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Back-of-Envelope Estimation)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### 基础假设 (Assumptions)

- DAU (Daily Active Users): 10 亿 (1B)
- 每用户每天平均观看: 5 个视频
- 每日视频播放量: $5 \times 10^9 = 50$ 亿次
- 每天新上传视频: 50 万 (500K)
- 视频平均时长: 7 分钟 (420 秒)
- 创作者与观众比例: 1:2000

### QPS 估算 (QPS Estimation)

**视频播放 QPS (读取)**:

$$QPS_{read} = \frac{5 \times 10^9}{86400} \approx 58,000$$

**峰值 QPS** (峰值倍数 3x):

$$QPS_{peak\_read} = 58,000 \times 3 = 174,000$$

**视频上传 QPS (写入)**:

$$QPS_{upload} = \frac{500,000}{86400} \approx 6$$

上传 QPS 极低，但每次上传涉及大量数据传输和后续转码，是 CPU/IO 密集型操作。

**片段请求 QPS** (每次播放请求约 60 个片段):

$$QPS_{segments} = 174,000 \times 60 = 10,440,000 \approx 10M$$

这是 CDN 需要承载的峰值请求量。

### 存储估算 (Storage Estimation)

**原始视频存储 (每天)**:

$$Storage_{raw/day} = 500,000 \times 7 \min \times 60 \frac{s}{\min} \times 5 \frac{MB}{s} \approx 1,050 \text{ TB/day}$$

(假设原始视频平均码率 40 Mbps = 5 MB/s)

**转码后存储** (6 种分辨率，总码率约为原始的 3 倍):

$$Storage_{transcoded/day} = 1,050 \times 3 = 3,150 \text{ TB/day}$$

**年存储量**:

$$Storage_{year} = (1,050 + 3,150) \times 365 = 1,533,000 \text{ TB} \approx 1.5 \text{ EB}$$

**存储优化后** (冷存储 + 删除低质量长尾视频的高分辨率版本):
实际存储约为理论值的 40%，即 **~600 PB/年**。

### 带宽估算 (Bandwidth Estimation)

**出站带宽 (视频播放)**:

假设平均观看码率 4 Mbps (720p H.264):

$$BW_{out} = 174,000 \times 4 \text{ Mbps} = 696 \text{ Gbps}$$

峰值约 **700 Gbps** 出站带宽，这是 CDN 的核心成本。

**CDN 缓存命中后的源站带宽** (假设 CDN 命中率 95%):

$$BW_{origin} = 700 \times 0.05 = 35 \text{ Gbps}$$

### 转码集群估算 (Transcoding Cluster)

**每日转码工作量**:

$$Transcode_{hours/day} = 500,000 \times 7 \min \times 6 \text{ resolutions} \times \frac{1}{60} = 350,000 \text{ hours}$$

(假设转码速度 = 1x 实时速度)

**需要的 Worker 数量** (每天 24 小时，利用率 70%):

$$Workers = \frac{350,000}{24 \times 0.7} \approx 20,833 \approx 21,000$$

使用 GPU 加速 (NVENC)，转码速度可达 5-10x 实时:

$$Workers_{GPU} = \frac{21,000}{7} = 3,000 \text{ GPU Workers}$$

### 内存估算 (Cache/Memory)

**视频元数据缓存 (Redis)**:

$$Memory_{metadata} = 10^9 \times 0.2 \times 2 \text{ KB} = 400 \text{ GB}$$

(缓存前 20% 热门视频的元数据，每条约 2 KB)

**观看计数缓存 (Redis)**:

$$Memory_{view\_count} = 10^9 \times 0.01 \times 16 \text{ bytes} = 160 \text{ MB}$$

(缓存前 1% 活跃视频的计数器)

### 核心算法: 自适应码率选择 (ABR Algorithm)

客户端 ABR 算法 (如 **BBA, Buffer-Based Approach**) 的核心逻辑:

$$R_{next} = \begin{cases}
R_{max} & \text{if } B > B_{high} \\
R_{prev} & \text{if } B_{low} \leq B \leq B_{high} \\
R_{min} & \text{if } B < B_{low}
\end{cases}$$

其中:
- $R_{next}$: 下一片段选择的码率
- $B$: 当前缓冲区时长 (秒)
- $B_{high}$, $B_{low}$: 缓冲区高低水位阈值 (典型值: 30s, 10s)

更先进的算法如 **MPC (Model Predictive Control)** 使用带宽预测:

$$\max \sum_{k=1}^{K} \left[ q(R_k) - \lambda \cdot \max(0, R_k - R_{k-1}) - \mu \cdot \max(0, T_{rebuf,k}) \right]$$

其中 $q(R_k)$ 是质量分数, $\lambda$ 是切换惩罚, $\mu$ 是卡顿惩罚。

### 容量总结

| 指标 | 数值 |
|------|------|
| DAU | 10 亿 |
| 日播放量 | 50 亿次 |
| 播放峰值 QPS | 174,000 |
| CDN 片段请求峰值 | 10M QPS |
| 每日新上传视频 | 50 万 |
| 日存储增长 (优化后) | ~1.7 PB |
| CDN 出站峰值带宽 | 700 Gbps |
| 源站带宽 (CDN 命中后) | 35 Gbps |
| 转码 GPU Workers | ~3,000 |
| Redis 元数据缓存 | 400 GB |
| 月成本估算 | ~$80M (CDN 占 60%) |
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Scale & Reliability)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 深度剖析: 规模与可靠性 (Deep Dive: Scale & Reliability)

### 规模数据 (Scale Numbers)

| 维度 | 数值 |
|------|------|
| 总视频数 | 10 亿+ (1B+) |
| 总存储 | ~2 EB (含多分辨率版本) |
| DAU | 10 亿 |
| 峰值同时观看 | 5000 万 |
| CDN 全球节点 | 200+ POP |
| 转码集群 | 3,000+ GPU Workers |
| MySQL 读副本 | 20+ 实例 |
| Redis 集群 | 40+ 节点 (400 GB) |

### 单点故障分析 (Single Point of Failure Analysis)

| 组件 | 风险 | 缓解策略 |
|------|------|---------|
| CDN 提供商 | 单一 CDN 故障影响全球播放 | 多 CDN 策略 (Primary: CloudFront, Fallback: Akamai), DNS 级别切换 |
| Object Storage (S3) | 极低概率但影响巨大 | 跨区域复制 (Cross-Region Replication), 双云备份关键内容 |
| MySQL 主库 | 写入不可用 | 主从切换 (MHA/Orchestrator), RTO < 30s |
| Kafka | 消息丢失或积压 | 3 副本, ISR (In-Sync Replicas) >= 2, 多 AZ 部署 |
| 转码管道 | 新视频无法上线 | 优先级队列 (头部创作者优先), 降级为仅转码 720p |
| Redis 缓存 | 缓存雪崩 | Sentinel 自动故障转移, 本地 L1 缓存兜底, 随机 TTL 防集中失效 |

### 多数据中心 / 跨区域 (Multi-DC / Cross-Region)

**部署拓扑**: 3 个主区域 (北美、欧洲、亚太) + 200+ CDN 边缘节点

**Active-Active 策略**:
- **视频播放**: 完全 Active-Active。CDN 就近路由，元数据从本区域 MySQL
  Read Replica 读取。所有区域都能独立服务播放请求
- **视频上传**: 上传到最近区域的 S3 Bucket，转码在该区域完成。
  转码产物通过 **S3 Cross-Region Replication** 同步到其他区域
- **元数据写入**: 单主 (Primary Region)，异步复制到其他区域。
  写入延迟对上传场景可接受 (~200ms 跨区域延迟)

**数据复制策略**:
- **视频文件**: 异步复制。热门视频 (前 1%) 预复制到所有区域;
  长尾视频按需从源区域拉取 + CDN 缓存
- **元数据**: **半同步复制** (至少一个从库确认后返回)，保证不丢数据
- **观看计数**: 最终一致。每个区域维护本地计数，每 5 分钟汇总到中心

**DNS 路由**:
- **GeoDNS** (如 Route 53) 将用户路由到最近区域
- 健康检查: 每 10 秒探测各区域端点，故障时自动切换
- Anycast IP 用于 CDN 边缘节点

**冲突解决**:
- 元数据写入: 单主架构避免写冲突
- 观看计数: CRDT (Conflict-free Replicated Data Type) G-Counter，
  多区域并发递增无冲突

### 高并发处理 (High Concurrency Handling)

**连接池 (Connection Pooling)**:
- API Server -> MySQL: **PgBouncer** (每实例 100 连接,
  30 个 API Server = 3000 活跃连接)
- API Server -> Redis: 每实例 50 连接的连接池

**限流 (Rate Limiting)**:
- 上传: 每用户每天 50 个视频
- 播放 API: 每用户 100 QPS (防爬虫)
- 搜索: 每用户 20 QPS
- 使用 **Token Bucket** 算法，状态存储在 Redis

**熔断器 (Circuit Breaker)**:
- Transcoding Service: 如果转码失败率 > 30%，熔断并降级为仅转码 720p
- Recommendation Service: 熔断后返回热门视频兜底列表
- Content Moderation: 熔断后允许上传但标记为 "pending review"

**优雅降级 (Graceful Degradation)**:

| 级别 | 触发条件 | 措施 |
|------|---------|------|
| L1 (正常) | CDN 命中率 > 90% | 全功能 |
| L2 (轻度压力) | CDN 命中率 70-90% | 关闭 4K 自动转码, 推荐结果缓存延长到 30 分钟 |
| L3 (中度压力) | 源站 QPS > 阈值 | 仅提供 720p 以下, 禁止新上传, 搜索结果缓存 1 小时 |
| L4 (严重压力) | 多区域故障 | 仅提供已缓存内容, 返回 "稍后再试" 给未缓存请求 |

### 监控与告警 (Monitoring & Alerting)

**关键指标**:
- **视频启动时间 (TTFB, Time to First Byte)**: P50 < 100ms, P99 < 500ms
- **缓冲率 (Rebuffering Rate)**: < 0.5% 的播放会话发生卡顿
- **CDN 缓存命中率**: > 90% (L1 边缘), > 98% (L1+L2 合计)
- **转码延迟**: P50 < 5 min, P99 < 30 min
- **上传成功率**: > 99.5%
- **错误率**: 5xx < 0.01% (播放 API)

**告警规则**:
- TTFB P99 > 1s 持续 5 分钟 -> PagerDuty 告警
- 缓冲率 > 2% -> 自动触发 L2 降级
- 转码队列积压 > 10 万 -> 自动扩容 GPU Worker
- CDN 命中率 < 80% -> 检查缓存配置和热点 key
"""

# ---------------------------------------------------------------------------
# S6: Tradeoffs
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡讨论 (Trade-off Discussion)

### 关键设计决策 (Key Design Decisions)

| 决策 | 选项 A | 选项 B | 我们的选择与理由 |
|------|--------|--------|----------------|
| 转码策略 | 预转码所有分辨率 (Eager) | 按需转码 (JIT) | **混合**: 热门创作者预转码全分辨率; 长尾视频仅预转码 480p+720p, 其余 JIT。节省 60% 存储成本 |
| CDN 架构 | 单一 CDN | 多 CDN | **多 CDN**: Primary (CloudFront) + Fallback (Akamai)。单 CDN 故障影响全球; 多 CDN 增加成本 15% 但消除单点故障 |
| 视频编码 | H.264 (兼容性最好) | AV1 (压缩率最高) | **渐进迁移**: 新内容同时提供 H.264 + AV1; AV1 压缩率比 H.264 好 30-50%, 但编码速度慢 10x, 需要 GPU。2-3 年内逐步淘汰 H.264 |
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
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Follow-up Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

### Q1: 如果一个视频突然爆火 (Viral)，比如从 0 到 1 亿播放，系统怎么应对?

**承认挑战**: 突发热门视频 (Thundering Herd) 是视频平台最经典的场景之一。
如果该视频尚未缓存在 CDN 边缘节点，所有请求会穿透到源站。

**缓解措施**:
1. **CDN Shield Layer**: L2 区域 Shield 吸收回源请求。即使 100 个边缘节点
   同时缓存未命中，Shield 只向源站发送 1 次请求，其他节点等待 Shield 的响应
   (**Request Coalescing / Origin Shield**)
2. **主动预热 (Proactive Warm-up)**: 当视频在 10 分钟内播放量增长 100x 时，
   系统自动将该视频的全分辨率版本推送到全球 TOP 20 CDN 节点
3. **源站限流**: 即使 Shield 也无法完全挡住，源站通过排队 + 限流保护自己，
   客户端重试策略 (指数退避 + 抖动)
4. **JIT 快速转码**: 如果该视频是长尾视频 (只有 480p/720p)，突然需要 1080p/4K，
   优先级队列中紧急转码，预计 2-5 分钟完成

**数据支撑**: Netflix 的 Open Connect 论文显示，Shield 层可以将源站流量
降低 95%。即使 1 亿请求/小时的突发，源站实际承受约 500 万请求/小时。

### Q2: 转码管道的一个 Worker 失败了怎么办? 会不会出现半转码的视频?

**承认风险**: 转码是长时间任务 (7 分钟视频约需 5-10 分钟转码)，Worker 崩溃
是常见故障。

**缓解措施**:
1. **幂等性 (Idempotency)**: 每个转码任务有唯一 task_id。Worker 崩溃后，
   Temporal/Airflow 自动重试。重复转码产物覆盖写入 S3 (幂等)
2. **片段级粒度 (Segment-level Granularity)**: 视频被分为 100+ 片段，
   每个片段独立转码。Worker 失败只影响该片段，不影响已完成的片段。
   重试只需重新转码失败的片段
3. **状态追踪**: 每个片段的转码状态记录在 Temporal Workflow 中:
   `{segment_id, status: pending/running/done/failed, worker_id, retry_count}`
4. **原子发布**: 只有所有分辨率的所有片段都完成，才生成 manifest 文件并更新
   MySQL status = "ready"。不会出现 "1080p 只有前半段" 的情况
5. **超时保护**: 单片段转码超时 5 分钟 (正常 < 30 秒) 自动标记为 failed 并重试

### Q3: 如果两个用户同时上传完全相同的视频 (重复内容), 系统如何处理?

**方案: 内容去重 (Content Deduplication)**:
1. 上传完成后计算视频的**内容指纹 (Content Fingerprint)**:
   - 音频指纹: **Chromaprint** 算法，生成 128 bit 指纹
   - 视频指纹: 从均匀采样的 N 帧中提取 **pHash (Perceptual Hash)**，
     容忍轻微裁剪/压缩差异
2. 指纹与数据库中已有视频比对:
   - 精确匹配: 共享同一份转码产物 (Copy-on-Write)，节省存储
   - 近似匹配 (相似度 > 95%): 标记为疑似重复，触发版权检测流程
3. **注意**: 去重仅影响存储层。每个上传者仍然有独立的 video_id 和元数据，
   可以有不同的标题、描述。对用户透明

**数据支撑**: YouTube 的实践显示，约 30% 的上传内容与已有视频存在
重复或近似重复。去重可以节省约 20% 的存储成本。

### Q4: 如果 CDN 全球某个区域宕机 (比如亚太区 Akamai 故障), 怎么处理?

**多层故障转移策略**:
1. **DNS 级别切换**: GeoDNS 健康检查检测到亚太区 Akamai 不可达后 (TTL 30s),
   将亚太用户路由到 CloudFront 亚太节点 (Fallback CDN)
2. **客户端级别切换**: 播放器内置 CDN Fallback 列表。如果主 CDN URL 连续
   3 次失败 (超时 2s)，自动切换到备用 CDN URL
3. **Origin Direct**: 极端情况下，播放器可以直接从源站 (S3 + Load Balancer)
   获取内容。延迟会增加但可用性保证
4. **预加载策略**: 播放器会提前缓冲 30 秒视频。CDN 切换的 10-30 秒内，
   用户感知不到中断 (缓冲区兜底)

**恢复时间**: DNS TTL 30s + 客户端探测 6s = **最坏情况 36 秒**。
期间缓冲区提供无缝播放体验。

### Q5: 如果流量突然 10x (比如某个大型体育赛事的精彩回放), 系统如何表现?

**自动扩缩容策略**:
1. **CDN**: 天然弹性。CDN 提供商 (CloudFront/Akamai) 的边缘容量
   远超任何单一客户的峰值。这是选择 CDN 而非自建的核心原因
2. **API Server**: 无状态, K8s HPA 基于 QPS 自动扩容。
   从 30 Pod 扩到 300 Pod 约 3-5 分钟
3. **Redis**: 短期依赖已有容量。Redis Cluster 支持动态添加节点，
   但 resharding 需要时间。提前按 2x 预留容量
4. **MySQL Read Replica**: 自动 Scaling 较慢 (~10 分钟启动新实例)。
   通过 Redis 缓存吸收峰值读取
5. **转码管道**: 10x 上传不太可能发生 (创作者数量有限)。
   如果确实需要，GPU Spot Instance 可以在 5 分钟内扩容

**降级方案** (如果扩容不够快):
- 推荐系统降级为热门列表 (不做个性化计算)
- 搜索结果缓存 TTL 从 30 秒延长到 10 分钟
- 非核心 API (评论、推荐) 限流 50%
- 视频质量限制为 720p (减少 CDN 带宽)

**准备措施**: 对于可预期的高峰 (Super Bowl, World Cup),
提前 48 小时预热 CDN (将相关视频推送到全球边缘) + 预扩容 API Server 2x。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1-Hour Interview Pacing Guide)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 面试节奏指南 (1-Hour Interview Pacing Guide)

### 3 分钟电梯演讲版 (Elevator Pitch)

"视频流媒体平台的核心挑战是: 10 亿 DAU 每天 50 亿次播放, 需要低延迟、
高可用的全球视频分发。我的方案分为两条管道:

1) **上传管道**: 断点续传 -> Kafka 任务队列 -> Temporal 转码工作流
   (视频分段 -> 并行 GPU 转码 -> HLS/DASH manifest 生成) -> S3 存储

2) **播放管道**: GeoDNS 就近路由 -> CDN 三层缓存 (L1 边缘 200+ POP ->
   L2 区域 Shield -> L3 源站 S3) -> ABR 自适应码率播放

关键设计:
- **混合转码**: 热门创作者全分辨率预转码; 长尾视频仅 480p+720p, 其余 JIT
- **多 CDN**: CloudFront (Primary) + Akamai (Fallback), DNS 级别故障转移
- **观看计数**: Redis 实时近似 + Cassandra 持久化 + T+1 精确批处理校准

规模: 10 亿 DAU, 174K 峰值播放 QPS, 10M CDN 片段 QPS,
700 Gbps CDN 出站带宽, 3,000 GPU 转码 Worker, 月成本 ~$80M。"

### 完整 1 小时面试节奏

#### 0-5 分钟: 需求澄清

**开场**: "视频流媒体有两个核心维度需要权衡:
上传处理延迟 vs 播放质量, 以及存储成本 vs 用户体验。让我先确认几个关键问题。"

**必须澄清的问题**:
1. "是 UGC 平台 (YouTube) 还是专业内容 (Netflix)? UGC 需要内容审核管道"
2. "需要支持直播吗? 我假设只做点播 (VOD), 直播是另一个设计题"
3. "目标覆盖全球还是特定市场? 我按全球 200+ CDN 节点规划"
4. "视频平均时长? 我按 7 分钟 (YouTube 风格) 估算"

**画出需求框架**:
```
FR: 上传 + 断点续传, 转码 (多分辨率), ABR 播放, 搜索, 社交互动
NFR: 174K peak QPS, TTFB < 200ms, 99.99% 可用, 零数据丢失
```

#### 5-15 分钟: 高层架构

**画两条管道**:

"上传管道 (Write Path)":
```
Client -> Presigned URL -> S3 -> Kafka -> Temporal Workflow
  -> Split -> Parallel GPU Transcode -> Merge -> HLS/DASH -> S3
  -> Update MySQL (status=ready) -> Notify Creator
```

"播放管道 (Read Path)":
```
Client -> GeoDNS -> CDN L1 (Edge 200+ POP)
  -> CDN L2 (Shield, 3 regions)
  -> CDN L3 (Origin S3)
  -> ABR: client picks quality based on bandwidth
```

**逐层解释**:
- **为什么用 Presigned URL?** "大文件上传不经过 API Server, 直接传到 S3,
  避免 API Server 成为瓶颈"
- **为什么用 Temporal?** "转码是长时间 (5-10 分钟) 多步骤工作流,
  需要重试、超时、状态追踪。Temporal 提供持久化工作流语义"
- **为什么三层 CDN?** "L1 吸收 90%+ 请求; L2 Shield 做 Request Coalescing
  防止回源风暴; L3 是终极兜底"

**数据库选择**:
- "MySQL 存元数据 (结构化, 需要事务), Redis 缓存热数据,
  Elasticsearch 做搜索, Cassandra 存观看事件, S3 存视频文件"
- "为什么不用 NoSQL 存元数据? 视频元数据需要复杂查询
  (按时间、类目、上传者), 关系型数据库更合适"

#### 15-25 分钟: 深度剖析 -- 转码管道

**核心挑战**: "7 分钟视频 x 6 种分辨率 x 多种编码 = 大量并行计算"

**详细解释**:
1. "视频按 GOP 边界分段, 每段约 4 秒。7 分钟 = 105 段"
2. "每段独立转码为 6 种分辨率, 使用 FFmpeg + NVENC GPU 加速"
3. "片段级重试: Worker 崩溃只影响 1 个片段, 不需要从头转码"
4. "原子发布: 所有片段完成后才生成 manifest 和更新 DB"

**容量**: "每天 50 万视频 -> 350,000 转码小时 -> 3,000 GPU Worker"

#### 25-35 分钟: 深度剖析 -- CDN 与 ABR

**CDN 架构详解**:
- "三层缓存: Edge (热门片段) -> Shield (Request Coalescing) -> Origin (S3)"
- "多 CDN 策略: CloudFront primary, Akamai fallback, DNS 30s 切换"
- "缓存策略: manifest TTL 60s (快速切换分辨率), 片段 TTL 24h (内容不变)"

**ABR 算法**:
- "Buffer-Based Approach: 缓冲区 > 30s 选高码率, < 10s 降低码率"
- "目标: 最大化质量 (高码率), 同时最小化卡顿 (rebuffering)"

#### 35-45 分钟: 深度剖析 -- 突发热门处理

**Viral Video 场景**:
- "Shield 做 Request Coalescing: 100 个边缘节点缓存未命中,
  只有 1 个请求到源站"
- "自动预热: 播放量 10 分钟增长 100x, 主动推送到全球 TOP 20 节点"
- "长尾视频的 JIT 转码: 紧急转码 1080p/4K, 优先级队列, 2-5 分钟"

#### 45-50 分钟: 权衡讨论

**3 个核心决策**:
1. "预转码 vs JIT: 混合策略, 热门全预转码, 长尾按需, 节省 60% 存储"
2. "H.264 vs AV1: 渐进迁移, AV1 省 30-50% 带宽但编码慢 10x"
3. "精确计数 vs 近似: 展示用近似, 创作者收益 T+1 精确结算"

**10x/100x**: "10x 需要自建 CDN 节点 (参考 Netflix Open Connect);
100x 需要自建骨干网 + 专用转码 ASIC"

#### 50-55 分钟: 收尾

**我会改进什么**:
- 添加 **DRM (Digital Rights Management)**: Widevine (Android/Chrome),
  FairPlay (Apple), PlayReady (Windows)
- 实现 **短视频优化**: < 60 秒的视频用不同的缓存和转码策略
- 添加 **用户端质量监控 (QoE Metrics)**: 每个播放会话上报
  TTFB、缓冲率、平均码率，用于实时质量优化

**监控清单**:
- 视频启动时间 (TTFB)
- 缓冲率 (Rebuffering Rate)
- CDN 缓存命中率
- 转码延迟和成功率
- 观看完成率 (completion rate)

#### 55-60 分钟: 向面试官提问

- "你们的视频平台用什么编码格式? 是否已经迁移到 AV1?"
- "CDN 是自建还是用第三方? 如果是自建，在多少个 POP 部署?"
- "转码管道最大的运维挑战是什么? 是 GPU 利用率还是长尾延迟?"

---

### 面试核心要点总结

关键设计决策:
- **两条管道**: 上传/转码管道 (写入) 和 CDN/ABR 播放管道 (读取) 解耦
- **三层 CDN 缓存**: Edge (200+ POP) -> Shield (Request Coalescing) -> Origin (S3)
- **DAG 转码工作流**: 视频分段 -> 并行 GPU 转码 -> 原子发布
- **混合转码策略**: 热门全预转码, 长尾按需 JIT, 节省 60% 存储
- **多 CDN 故障转移**: Primary + Fallback, DNS 30s 切换, 客户端自动重试

规模: 10 亿 DAU, 50 亿日播放, 174K 峰值 QPS, 10M CDN 片段 QPS,
700 Gbps 出站带宽, 3,000 GPU Worker, ~$80M/月。
"""


def populate_interview_video_streaming() -> None:
    """Create or update the interview-video-streaming record with all 8 sections."""
    init_db()
    db = SessionLocal()

    try:
        record = (
            db.query(SystemDesign)
            .filter(SystemDesign.slug == SLUG)
            .first()
        )

        if record is None:
            record = SystemDesign(
                slug=SLUG,
                title=TITLE,
                display_order=DISPLAY_ORDER,
            )
            db.add(record)
            db.flush()
            print(f"[DONE] Created SystemDesign record: slug='{SLUG}', title='{TITLE}'")
        else:
            print(f"[INFO] Found existing record for slug='{SLUG}', updating...")

        record.overview = OVERVIEW
        record.architecture = ARCHITECTURE
        record.dataflow = DATAFLOW
        record.formulas = FORMULAS
        record.production_constraints = PRODUCTION_CONSTRAINTS
        record.tradeoffs = TRADEOFFS
        record.defense = DEFENSE
        record.verbal_outline = VERBAL_OUTLINE

        db.commit()
        print(f"[DONE] Updated all 8 sections for '{SLUG}'.")

        # Verify by re-reading
        db.refresh(record)
        sections = [
            ("overview", record.overview),
            ("architecture", record.architecture),
            ("dataflow", record.dataflow),
            ("formulas", record.formulas),
            ("production_constraints", record.production_constraints),
            ("tradeoffs", record.tradeoffs),
            ("defense", record.defense),
            ("verbal_outline", record.verbal_outline),
        ]
        total_chars = 0
        for name, content in sections:
            length = len(content) if content else 0
            total_chars += length
            status = "[OK]" if length > 100 else "[WARN] short"
            print(f"  {status} {name}: {length} chars")
        print(f"  Total: {total_chars} chars")

        # Check for Chinese characters
        chinese_pattern = re.compile(r"[\u4e00-\u9fff]")
        for name, content in sections:
            if content and chinese_pattern.search(content):
                print(f"  [OK] {name}: Chinese chars present")
            else:
                print(f"  [WARN] {name}: No Chinese chars found!")

        # Check for bare | in math
        bare_pipe = False
        for name, content in sections:
            if not content:
                continue
            in_math = False
            for i, ch in enumerate(content):
                if ch == "$" and (i == 0 or content[i - 1] != "\\"):
                    in_math = not in_math
                if in_math and ch == "|" and (i == 0 or content[i - 1] != "\\"):
                    before = content[max(0, i - 4):i]
                    if "\\mid" not in before and "\\vert" not in before:
                        bare_pipe = True
                        print(f"  [WARN] {name}: bare | found in math near position {i}")

        if not bare_pipe:
            print("  [OK] No bare | in math formulas")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_interview_video_streaming()
