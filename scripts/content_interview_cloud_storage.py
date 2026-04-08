"""Populate interview-cloud-storage system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design Dropbox/Google
Drive -- block-level chunking & dedup, delta sync, conflict resolution,
metadata DB, sync notification, storage optimization, and offline editing.
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

SLUG = "interview-cloud-storage"
TITLE = "Design Dropbox/Google Drive"
DISPLAY_ORDER = 113

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个**云端文件存储与同步服务 (Cloud File Storage & Sync Service)**，类似
Dropbox 或 Google Drive。用户可以在任意设备上上传、下载、编辑文件，系统自动
在所有设备之间保持文件同步。核心挑战在于：(1) 大文件传输效率，(2) 多设备冲突
检测与解决，(3) 海量小文件元数据管理，(4) 离线编辑与重新上线后的增量同步。

云存储是典型的"读多写多"系统 -- 不同于社交媒体的"写少读多"，用户在本地频繁
修改文件，每次修改都需要同步到云端并通知其他设备。这要求系统在**一致性、延迟
和带宽效率**之间取得精确平衡。

### 功能性需求 (Functional Requirements)

1. **文件上传 (Upload)**: 用户上传文件到云端，支持最大 50 GB 单文件，
   支持**断点续传 (Resumable Upload)**
2. **文件下载 (Download)**: 从云端下载文件到本地设备
3. **自动同步 (Auto Sync)**: 本地文件修改后自动检测变更并同步到云端，
   其他设备自动拉取最新版本
4. **文件分享 (Sharing)**: 生成分享链接，支持只读/可编辑权限
5. **版本历史 (Version History)**: 保留文件的历史版本 (至少 30 天)，
   支持回滚到任意历史版本
6. **离线编辑 (Offline Editing)**: 无网络时本地编辑，重新联网后自动同步

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**: 99.99% -- 文件丢失对用户是灾难性的
- **持久性 (Durability)**: 11 个 9 (99.999999999%) -- 数据零丢失
- **延迟 (Latency)**: 小文件 (< 1 MB) 同步延迟 < 500ms；
  大文件开始传输 < 1s
- **一致性 (Consistency)**: 文件元数据强一致 (同一用户的所有设备看到相同
  文件列表)；文件内容最终一致 (允许短暂的传输延迟)
- **带宽效率 (Bandwidth Efficiency)**: 只传输变更部分，不传输整个文件
  (**Delta Sync，增量同步**)
- **可扩展性 (Scalability)**: 支持 5 亿用户，每用户平均 200 个文件

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 文件类型是否有限制? 是通用文件还是特定类型 (如文档、图片)?**
   -- WHY: 通用文件需要 block-level chunking；特定类型 (如 Google Docs)
   可以用 **OT (Operational Transformation)** 做字符级实时协作

2. **Q: 是否需要实时协同编辑 (Real-time Collaboration)?**
   -- WHY: 实时协编 (如 Google Docs) 需要 **CRDT (Conflict-free Replicated
   Data Types)** 或 OT 引擎，架构完全不同于文件级同步

3. **Q: 用户的平均文件大小和文件数量是多少?**
   -- WHY: 影响 chunking 策略。大文件 (视频/设计稿) 需要更大的 chunk size；
   海量小文件 (代码仓库) 需要高效的元数据索引

4. **Q: 删除文件后是否可以恢复? 保留多久?**
   -- WHY: 决定 soft delete 策略和存储成本。Dropbox 保留 30 天，
   Google Drive 30 天回收站

5. **Q: 需要支持多少种平台 (Windows, macOS, Linux, iOS, Android, Web)?**
   -- WHY: 桌面客户端可以监听文件系统事件 (inotify/FSEvents)；
   移动端和 Web 需要不同的同步策略

6. **Q: 是否需要端到端加密 (E2E Encryption)?**
   -- WHY: E2E 加密意味着服务端无法读取文件内容，会影响去重和搜索功能。
   Dropbox 不做 E2E；iCloud 对部分数据做 E2E

7. **Q: 企业版是否需要管理员控制 (Admin Console)?**
   -- WHY: 企业功能 (审计日志、DLP、设备管理) 是独立子系统，
   本次设计先聚焦个人版核心同步功能

### 范围界定 (Out of Scope)

- 实时协同编辑 (Google Docs 风格) -- 属于独立系统设计题目
- 企业管理控制台 (Admin Console)
- 全文搜索 (文件内容搜索)
- 照片/视频智能分类 (Google Photos 功能)
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 高层架构 (High-Level Architecture)

### 组件总览 (Component Overview)

系统分为**客户端 (Desktop/Mobile Client)**和**服务端 (Cloud Backend)**两大部分。
客户端负责本地文件监控、chunking、差异计算；服务端负责存储、元数据管理、
同步协调和通知推送。

```
[Desktop Client]
  |-- File Watcher (inotify/FSEvents)
  |-- Chunker (块分割引擎)
  |-- Delta Engine (差异计算)
  |-- Local DB (SQLite)
  |
  v
[API Gateway / Load Balancer]
  |
  +--------+---------+---------+
  |        |         |         |
[Sync   [Upload  [Sharing  [Notification
 Service] Service] Service]  Service]
  |        |         |         |
  v        v         v         v
[Metadata DB]  [Block Store]  [Message Queue]
(MySQL/        (S3/GCS)       (Kafka)
 PostgreSQL)
  |
[Block Dedup Index]
(Redis / Cassandra)
```

### 核心服务及职责 (Core Services)

#### 1. Client-Side Components (客户端组件)

- **File Watcher (文件监控器)**: 监听本地同步文件夹的文件系统事件
  - macOS: **FSEvents** API，粒度到文件级变更
  - Windows: **ReadDirectoryChangesW** API
  - Linux: **inotify** API
  - 检测: 创建、修改、删除、重命名、移动
- **Chunker (分块引擎)**: 将文件分割为固定大小或**内容感知 (Content-Defined
  Chunking, CDC)** 的数据块
  - **CDC 算法**: 使用 **Rabin Fingerprint (拉宾指纹)** 滑动窗口在内容边界处
    切分，平均 chunk size 4 MB (范围 2-8 MB)
  - CDC 优势: 文件中间插入内容只影响插入点附近的 chunk，不会导致后续所有
    chunk 偏移 (固定大小分块的致命缺陷)
- **Delta Engine (差异引擎)**: 计算修改后文件与上一版本之间的差异
  - 使用 **rsync 算法** 或 **librsync** 进行二进制差异计算
  - 只上传变更的 chunk，未变更的 chunk 通过 hash 匹配跳过
- **Local DB (本地数据库)**: SQLite 存储本地文件索引、chunk hash 列表、
  同步状态 (synced/pending/conflict)

#### 2. Sync Service (同步服务)

核心编排服务，处理客户端的同步请求:
- **上传同步**: 接收客户端的 chunk 列表 (hash + offset)，比对服务端版本，
  确定哪些 chunk 需要上传
- **下载同步**: 返回文件最新版本的 chunk 列表，客户端只下载本地缺失的 chunk
- **冲突检测**: 基于**版本向量 (Version Vector)** 检测多设备并发修改冲突
- **版本管理**: 每次文件修改创建新版本记录 (版本号递增)

#### 3. Upload Service (上传服务)

- 接收客户端上传的 chunk 数据
- **去重 (Deduplication)**: 上传前客户端发送 chunk hash 列表，
  服务端检查 Block Dedup Index，已存在的 chunk 跳过上传 (**秒传**)
- **断点续传**: 基于 chunk 粒度，中断后只需重传未完成的 chunk
- 大文件支持: 50 GB 文件 / 4 MB chunk = 12,800 chunks，并行上传 4-8 个 chunk

#### 4. Notification Service (通知服务)

- **长轮询 (Long Polling)** / **WebSocket**: 当文件在服务端被修改
  (另一设备同步上来)，实时通知其他在线设备
- **推送通知 (Push Notification)**: 移动设备通过 APNs/FCM 接收同步通知
- **变更日志 (Change Feed)**: 每个用户维护一个有序的变更事件流，
  设备通过游标 (cursor) 增量拉取

#### 5. Sharing Service (分享服务)

- 生成分享链接: 随机 token + 权限级别 (view/edit/comment)
- 权限模型: Owner > Editor > Viewer，支持设置密码和过期时间
- 协作文件夹: 多用户共享文件夹，每个用户独立同步

### 数据库选择与理由 (Database Choices)

| 数据类型 | 数据库 | 理由 |
|---------|--------|------|
| 文件/文件夹元数据 | MySQL + Read Replicas | 树形结构 (parent_id), 需要事务, ACID 保证 |
| Chunk 去重索引 | Redis (热) + Cassandra (冷) | hash -> location 查找, 极高 QPS, 最终一致即可 |
| 文件版本历史 | MySQL (同元数据库) | 与文件元数据强关联, 需要事务保证版本一致 |
| 文件内容 (Chunks) | S3 / GCS | 对象存储, 11 个 9 持久性, 按访问分层 |
| 变更事件流 | Kafka | 有序事件流, 高吞吐, 支持多消费者 |
| 用户会话/在线状态 | Redis | 低延迟读写, TTL 自动过期 |

### 通信模式 (Communication Patterns)

- **同步 (REST/gRPC)**: 文件元数据 CRUD, chunk 上传/下载, 权限管理
- **长连接 (WebSocket / Long Polling)**: 实时同步通知 (新文件、修改、删除)
- **异步 (Kafka)**: 变更事件广播, 去重索引更新, 审计日志
"""

# ---------------------------------------------------------------------------
# S3: API Design + Data Flow
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### REST API 端点 (REST API Endpoints)

#### 文件同步 -- 检查变更

```
POST /api/v1/sync/changes
Request: { "user_id": "u_123", "device_id": "dev_abc",
           "cursor": "c_2024010100001" }
Response: { "changes": [
              { "file_id": "f_001", "action": "modified",
                "version": 42, "chunks": ["hash1","hash2",...],
                "modified_at": "2024-01-15T10:30:00Z" },
              { "file_id": "f_002", "action": "deleted", "version": 5 }
            ],
            "cursor": "c_2024011510302", "has_more": false }
Status: 200 OK
```

#### 文件上传 -- 请求上传 URL

```
POST /api/v1/files/upload/init
Request: { "file_path": "/documents/report.pdf",
           "file_size": 104857600,
           "chunk_hashes": ["sha256:abc...", "sha256:def...", ...],
           "parent_version": 41 }
Response: { "upload_session_id": "up_xyz",
            "chunks_needed": [0, 3, 7],
            "chunks_existing": [1, 2, 4, 5, 6],
            "presigned_urls": {
              "0": "https://storage.example.com/upload/chunk_0?sig=...",
              "3": "https://storage.example.com/upload/chunk_3?sig=...",
              "7": "https://storage.example.com/upload/chunk_7?sig=..." } }
Status: 200 OK
```

#### Chunk 上传

```
PUT /api/v1/files/upload/{upload_session_id}/chunk/{chunk_index}
Request: [binary chunk data]
Response: { "chunk_index": 0, "status": "received",
            "checksum_verified": true }
Status: 200 OK
```

#### 提交文件版本

```
POST /api/v1/files/upload/{upload_session_id}/commit
Request: { "file_path": "/documents/report.pdf",
           "total_size": 104857600,
           "chunk_list": ["sha256:abc...", "sha256:def...", ...],
           "checksum": "sha256:full_file_hash" }
Response: { "file_id": "f_001", "version": 42,
            "status": "committed",
            "modified_at": "2024-01-15T10:30:00Z" }
Status: 201 Created
```

#### 文件下载

```
GET /api/v1/files/{file_id}/chunks?version=42
Response: { "file_id": "f_001", "version": 42,
            "total_size": 104857600,
            "chunks": [
              { "index": 0, "hash": "sha256:abc...", "size": 4194304,
                "url": "https://cdn.example.com/chunks/sha256_abc?sig=..." },
              ...
            ] }
Status: 200 OK
```

#### 文件分享

```
POST /api/v1/files/{file_id}/share
Request: { "permission": "view", "password": null,
           "expires_at": "2024-02-15T00:00:00Z" }
Response: { "share_link": "https://drive.example.com/s/Xk9mN2p",
            "permission": "view",
            "expires_at": "2024-02-15T00:00:00Z" }
Status: 201 Created
```

### 核心数据模型 (Core Data Models)

```sql
-- 文件/文件夹元数据
CREATE TABLE file_metadata (
    file_id         VARCHAR(20) PRIMARY KEY,
    user_id         VARCHAR(20) NOT NULL,
    parent_id       VARCHAR(20),              -- NULL = root folder
    name            VARCHAR(500) NOT NULL,
    is_folder       BOOLEAN DEFAULT FALSE,
    size_bytes       BIGINT DEFAULT 0,
    current_version INT DEFAULT 1,
    content_hash    VARCHAR(64),              -- SHA-256 of full file
    status          ENUM('active','trashed','deleted'),
    created_at      DATETIME NOT NULL,
    modified_at     DATETIME NOT NULL,
    INDEX idx_user_parent (user_id, parent_id),
    INDEX idx_user_status (user_id, status),
    UNIQUE INDEX idx_user_parent_name (user_id, parent_id, name)
);

-- 文件版本
CREATE TABLE file_versions (
    version_id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    file_id         VARCHAR(20) NOT NULL,
    version_num     INT NOT NULL,
    size_bytes      BIGINT,
    content_hash    VARCHAR(64),
    chunk_list      JSON,                     -- ordered list of chunk hashes
    device_id       VARCHAR(20),
    created_at      DATETIME NOT NULL,
    UNIQUE INDEX idx_file_version (file_id, version_num)
);

-- Chunk 去重索引
CREATE TABLE chunk_index (
    chunk_hash      VARCHAR(64) PRIMARY KEY,  -- SHA-256
    size_bytes      INT NOT NULL,
    ref_count       INT DEFAULT 1,            -- reference counting for GC
    storage_key     VARCHAR(200) NOT NULL,     -- S3 key
    created_at      DATETIME NOT NULL
);

-- 变更事件流
CREATE TABLE change_events (
    event_id        BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id         VARCHAR(20) NOT NULL,
    file_id         VARCHAR(20) NOT NULL,
    action          ENUM('create','modify','delete','rename','move','share'),
    version_num     INT,
    device_id       VARCHAR(20),
    created_at      DATETIME NOT NULL,
    INDEX idx_user_time (user_id, created_at)
);
```

### 写入路径: 文件修改同步 (Write Path)

1. **本地检测**: File Watcher 检测到 `report.pdf` 被修改
2. **分块计算**: Chunker 使用 CDC (Rabin Fingerprint) 重新分块
3. **差异比较**: 本地 DB 中查找上一版本的 chunk hash 列表，
   对比确定哪些 chunk 发生变化 (通常只有 1-3 个 chunk)
4. **上传初始化**: 向 Sync Service 发送变更 chunk hash 列表
5. **去重检查**: 服务端查询 Block Dedup Index，返回需要实际上传的 chunk
   (已存在的 chunk 跳过 -- **秒传**)
6. **Chunk 上传**: 客户端通过 Presigned URL 直接上传到 S3
7. **版本提交**: 所有 chunk 上传完成后，提交新版本记录
   (原子操作: 更新 file_metadata.current_version + 插入 file_versions 记录)
8. **变更广播**: Sync Service 向 Kafka 发送变更事件
9. **通知推送**: Notification Service 通过 WebSocket/Long Polling
   通知该用户的其他在线设备
10. **设备同步**: 其他设备收到通知后，拉取变更的 chunk 列表，
    只下载本地缺失的 chunk，在本地重组文件

### 读取路径: 文件下载/同步 (Read Path)

1. **变更检测**: 设备上线后通过 cursor 拉取所有未同步的变更事件
2. **元数据获取**: 对每个变更的文件，获取最新版本的 chunk 列表
3. **本地比对**: 将服务端 chunk 列表与本地 chunk 缓存比对，
   确定需要下载的 chunk (增量下载)
4. **Chunk 下载**: 从 CDN / S3 并行下载缺失的 chunk (4-8 并行)
5. **文件重组**: 按 chunk 顺序重组文件，验证 full file checksum
6. **本地更新**: 更新本地 DB 的文件元数据和 chunk 缓存
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Back-of-Envelope Estimation + Core Algorithms)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### 容量估算 (Capacity Estimation)

**基础假设**:
- DAU: 1 亿 (100M)
- 注册用户: 5 亿 (500M)
- 每用户平均文件数: 200 个
- 平均文件大小: 500 KB (中位数，含大量小文档/图片)
- 大文件占比: 5% 的文件 > 100 MB
- 每日活跃修改: 每 DAU 平均修改 5 个文件/天
- 每次修改平均传输量: 原文件大小的 10% (Delta Sync 效果)

**存储容量**:

$$
\text{Total Files} = 500M \times 200 = 100B \text{ (1000 亿文件)}
$$

$$
\text{Total Storage} = 100B \times 500\text{KB} = 50\text{PB (Petabytes)}
$$

$$
\text{Daily New Storage} = 100M \times 5 \times 500\text{KB} \times 10\% = 25\text{TB/day}
$$

$$
\text{Version History (30 days)} = 25\text{TB} \times 30 = 750\text{TB}
$$

去重效果: 跨用户去重可节省约 30-40% 存储，有效存储约 **35 PB**。

**QPS 估算**:

$$
\text{Daily Sync Requests} = 100M \times 5 = 500M
$$

$$
\text{Avg QPS} = \frac{500M}{86400} \approx 5,800
$$

$$
\text{Peak QPS} = 5,800 \times 3 \approx 17,400
$$

Chunk 级 QPS (每次文件修改平均涉及 3 个 chunk):

$$
\text{Chunk Upload QPS (peak)} = 17,400 \times 3 \approx 52,000
$$

**元数据 QPS**:
- 文件列表查询 (打开文件夹): 每 DAU 平均 20 次/天
- 变更轮询: 每在线设备每 60 秒一次长轮询

$$
\text{Metadata QPS} = \frac{100M \times 20}{86400} + \frac{50M \times 1}{60} \approx 23,000 + 833,000 \approx 856,000
$$

元数据读取 QPS 远高于写入，读写比约 **50:1**。

**带宽估算**:

$$
\text{Daily Upload} = 100M \times 5 \times 500\text{KB} \times 10\% = 25\text{TB}
$$

$$
\text{Upload Bandwidth (avg)} = \frac{25\text{TB}}{86400} \approx 300\text{MB/s} = 2.4\text{Gbps}
$$

$$
\text{Upload Bandwidth (peak)} = 2.4 \times 3 = 7.2\text{Gbps}
$$

下载通常是上传的 2-3 倍 (多设备同步):

$$
\text{Download Bandwidth (peak)} \approx 7.2 \times 2.5 = 18\text{Gbps}
$$

**内存 (Cache)**:

$$
\text{Metadata Cache} = 100M \text{ DAU} \times 200 \text{ files} \times 500\text{B/record} = 10\text{TB}
$$

热数据 (当日活跃文件的元数据) 约占 5%:

$$
\text{Hot Cache} = 10\text{TB} \times 5\% = 500\text{GB Redis}
$$

### 核心算法 (Core Algorithms)

#### Content-Defined Chunking (CDC, 内容定义分块)

固定大小分块的问题: 在文件开头插入 1 字节，所有后续 chunk 边界偏移 1 字节，
导致**所有 chunk hash 变化**，整个文件需要重新上传。

CDC 使用 **Rabin Fingerprint** 滑动窗口:
- 窗口大小: 48 字节
- 对窗口内数据计算 Rabin 指纹 (多项式滚动哈希)
- 当指纹满足条件 (如低 13 位全为 0) 时，该位置为 chunk 边界

$$
\text{Expected chunk size} = 2^{13} = 8192 \text{ bytes (for 13-bit mask)}
$$

实际使用 22-bit mask，平均 chunk size 约 **4 MB**:

$$
\text{Average chunk} = 2^{22} = 4\text{MB}
$$

$$
\text{Min chunk} = 2\text{MB}, \quad \text{Max chunk} = 8\text{MB}
$$

**CDC 优势**: 文件中间插入内容只影响插入点附近 1-2 个 chunk，
其余 chunk hash 不变，Delta Sync 效率极高。

#### Deduplication (去重)

- 每个 chunk 计算 **SHA-256** hash (256 bits)
- 上传前查询 Block Dedup Index (Redis): hash 是否已存在
- 存在 -> 增加 ref_count，跳过上传 (秒传)
- 不存在 -> 上传到 S3，写入 Dedup Index

$$
\text{Collision probability (SHA-256)} = \frac{1}{2^{256}} \approx 10^{-77}
$$

实际发生碰撞的概率低于地球被陨石摧毁的概率，无需额外处理。

#### Version Vector (版本向量)

每个文件在每个设备上维护一个版本向量:

$$
VV = \{D_1: v_1, D_2: v_2, \ldots, D_n: v_n\}
$$

- $D_i$ = 设备 ID, $v_i$ = 该设备上的最新修改版本号
- 当 $VV_A$ 的每个分量都 $\geq$ $VV_B$ 对应分量时，A "happened after" B
- 当 $VV_A$ 和 $VV_B$ 互不包含时，检测到**冲突 (conflict)**

### 服务器规模估算 (Server Sizing)

| 组件 | 数量 | 规格 |
|-----|------|------|
| Sync Service | 50 pods | 4 vCPU, 8 GB RAM |
| Upload Service | 30 pods | 4 vCPU, 16 GB RAM |
| Notification Service | 20 pods | 2 vCPU, 4 GB RAM + 500K WebSocket 连接 |
| MySQL (Metadata) | 1 master + 10 replicas | 64 vCPU, 256 GB RAM, 10 TB SSD |
| Redis (Dedup Index) | 100 nodes cluster | 32 GB RAM each = 3.2 TB total |
| Redis (Metadata Cache) | 50 nodes cluster | 16 GB RAM each = 800 GB total |
| S3 Storage | - | ~35 PB (去重后) |
| Kafka | 20 brokers | 16 vCPU, 64 GB RAM, 4 TB NVMe |

**月成本估算**:
- S3 存储 (35 PB): ~$800K/month
- EC2/EKS (API + Workers): ~$200K/month
- 带宽 (18 Gbps peak): ~$300K/month
- MySQL RDS: ~$50K/month
- Redis: ~$80K/month
- Total: **~$1.5M/month**
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Scale & Reliability Deep Dive)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 深度剖析: 规模与可靠性 (Deep Dive: Scale & Reliability)

### 具体规模数据 (Concrete Scale Numbers)

| 指标 | 数值 |
|------|------|
| 注册用户 | 5 亿 |
| DAU | 1 亿 |
| 总文件数 | 1000 亿 |
| 总存储 (去重后) | 35 PB |
| 每日新增存储 | 25 TB |
| 峰值同步 QPS | 17,400 |
| 峰值 Chunk QPS | 52,000 |
| 元数据读 QPS | ~856,000 |
| 峰值下载带宽 | 18 Gbps |
| WebSocket 长连接 | 5000 万 |

### 单点故障分析 (Single Point of Failure Analysis)

#### Metadata DB (元数据数据库)

**风险**: MySQL Master 宕机 -> 所有写入停止，新文件无法同步。

**缓解措施**:
1. **Semi-Synchronous Replication**: Master 写入至少 1 个 Replica 确认后
   才返回成功，保证 RPO = 0
2. **自动 Failover**: 使用 **Orchestrator** 或 **MySQL Group Replication**，
   故障转移时间 < 30 秒
3. **分库 (Sharding)**: 按 user_id 分片 (Vitess / ProxySQL)，
   每个 shard 独立的 Master-Replica 组。单 shard 故障只影响部分用户

#### Block Store (S3)

**风险**: S3 本身极少全局故障 (历史仅 2017 年 us-east-1 事件)。

**缓解措施**:
1. **Cross-Region Replication (CRR)**: S3 对象自动复制到另一个 Region
2. **多云备份**: 关键数据 (如 chunk) 每周全量备份到 GCS (Google Cloud Storage)

#### Notification Service (通知服务)

**风险**: WebSocket 网关宕机 -> 在线设备收不到实时同步通知。

**缓解措施**:
1. **客户端降级**: WebSocket 断开后自动降级为 Long Polling (每 60 秒)
2. **多实例 + Consistent Hashing**: 用户连接按 user_id hash 分布到不同网关实例。
   单实例故障只影响 1/N 用户
3. **客户端重连**: 断线后 exponential backoff 重连 (1s, 2s, 4s, 8s, max 30s)

### 多数据中心 / 跨区域策略 (Multi-Datacenter Strategy)

#### Active-Passive 架构 (Dropbox 模式)

- **Primary Region**: us-west-2 (所有写入)
- **Passive Region**: eu-west-1 (只读副本，灾备)
- **数据复制**: MySQL 跨 Region 异步复制 (延迟 100-300ms)；
  S3 CRR 异步复制 (延迟 < 15 分钟)

#### 读取优化

- 元数据读取: 用户就近读取最近的 MySQL Replica
- 文件下载: CDN 就近分发 (CloudFront / Akamai)
- 同步通知: WebSocket 网关部署在多个 Region，就近连接

#### 故障转移

- Primary 全区宕机 -> DNS 切换到 Passive Region (TTL 60s)
- **RTO (Recovery Time Objective)**: < 5 分钟
- **RPO (Recovery Point Objective)**: < 1 分钟 (异步复制延迟)

### 高并发处理 (High Concurrency Handling)

#### 同一文件多设备并发修改

这是云存储最核心的难题:

1. **乐观锁 (Optimistic Locking)**:
   - 每次提交新版本时携带 `parent_version`
   - 服务端检查: 当前版本 == parent_version?
   - 是 -> 提交成功，版本号 +1
   - 否 -> 返回冲突，客户端需要处理

2. **冲突解决策略 (Conflict Resolution)**:
   - **Last Writer Wins (LWW)**: 最简单但可能丢失数据 (Google Drive 默认)
   - **创建冲突副本 (Conflict Copy)**: Dropbox 的做法 -- 保留两个版本，
     文件名加后缀 `(conflicted copy from Device-A 2024-01-15)`
   - **三方合并 (Three-Way Merge)**: 对文本文件，使用共同祖先版本做
     三方 diff，自动合并不冲突的修改 (类似 git merge)

3. **实践推荐**: 采用 Dropbox 模式 -- **创建冲突副本 + 用户手动解决**。
   原因: 二进制文件无法自动合并，冲突概率低 (< 0.01%)，
   用户手动解决最安全

#### 元数据高 QPS 处理

- **读取**: Redis 缓存 + MySQL Read Replicas (10 个)
  - 缓存策略: Read-Through，TTL 5 分钟
  - 缓存命中率: > 95% (热数据集中)
- **写入**: 按 user_id 分片到不同 MySQL Shard
  - 单 Shard 写入 QPS: 17,400 / 8 shards = ~2,200 QPS
  - MySQL 单实例写入能力: ~5,000 QPS，充足

#### 连接管理

- WebSocket: 每个网关实例维护 50 万连接，20 个实例 = 1000 万同时在线
- **Connection Pool**: 每个 Sync Service Pod 维护 10 个 MySQL 连接，
  50 pods = 500 连接 (MySQL max_connections 通常 1000-2000)

### 监控与告警 (Monitoring & Alerting)

**关键指标**:
- **同步延迟 (Sync Latency)**: P50 < 500ms, P99 < 2s -- 用户感知到的同步速度
- **冲突率 (Conflict Rate)**: < 0.01% -- 过高说明通知延迟或锁机制有问题
- **Chunk 去重率 (Dedup Hit Rate)**: 期望 30-40% -- 过低说明 CDC 参数需调优
- **WebSocket 连接数**: 监控每实例连接数，超过 80% 容量时自动扩容
- **S3 上传失败率**: < 0.01% -- 监控断点续传的重试次数
- **MySQL 复制延迟**: < 1 秒 -- 超过 5 秒告警
"""

# ---------------------------------------------------------------------------
# S6: Tradeoffs
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡讨论 (Trade-off Discussion)

### 关键设计决策 (Key Design Decisions)

| 决策 | 选项 A | 选项 B | 我们的选择与理由 |
|------|--------|--------|-----------------|
| 分块策略 | **固定大小分块** (4 MB) | **CDC (Content-Defined Chunking)** | CDC -- 文件中间插入不会导致所有后续 chunk 偏移，Delta Sync 效率从 O(文件大小) 降到 O(变更大小)。代价是 Rabin Fingerprint 计算开销 (~5% CPU)，但带宽节省远大于 CPU 成本 |
| 冲突解决 | **Last Writer Wins (LWW)** | **创建冲突副本 (Conflict Copy)** | 冲突副本 -- LWW 静默丢失数据是不可接受的。冲突概率 < 0.01%，创建副本的用户体验成本低于数据丢失风险。文本文件可叠加三方合并优化 |
| 通知机制 | **轮询 (Polling, 30s)** | **长连接 (WebSocket)** | WebSocket -- 轮询在 5000 万在线设备下 QPS = 1.67M，远高于 WebSocket 的事件驱动推送。WebSocket 内存成本 (~50 KB/连接) 在可接受范围 |
| 去重粒度 | **文件级去重 (Whole-file hash)** | **块级去重 (Chunk-level hash)** | 块级去重 -- 文件级去重只有完全相同的文件才能秒传；块级去重在文件部分相同时也能节省传输和存储。代价是去重索引更大 (chunk 数量 >> 文件数量) |
| 元数据存储 | **NoSQL (DynamoDB)** | **SQL (MySQL + Sharding)** | MySQL + Sharding -- 文件系统是树形结构，需要 parent-child 关系查询、事务保证 (重命名文件夹需要原子更新所有子节点)、强一致性。NoSQL 缺乏跨 partition 事务支持 |

### CAP 定理应用 (CAP Theorem Application)

云存储系统在不同组件上做了不同的 CAP 选择:

- **文件元数据**: **CP (Consistency + Partition Tolerance)**
  - 同一用户在所有设备上必须看到一致的文件列表
  - 网络分区时拒绝写入 (MySQL Master 不可达时写入失败)
  - 客户端降级为离线模式，本地队列暂存修改

- **文件内容 (Chunks)**: **AP (Availability + Partition Tolerance)**
  - chunk 上传后通过 S3 CRR 异步复制到其他 Region
  - 短暂的不一致可接受 (其他 Region 可能读到旧版本)
  - 最终一致: 复制延迟通常 < 15 分钟

- **通知服务**: **AP**
  - WebSocket 断开时降级为 Long Polling
  - 可能短暂延迟收到通知，但不会丢失 (基于 cursor 的变更流)

### 成本 vs 性能 (Cost vs Performance)

**热/冷分层存储策略**:
- 30 天内修改过的文件: S3 Standard ($0.023/GB/month)
- 30-90 天未修改: S3 Infrequent Access ($0.0125/GB/month, 节省 46%)
- 90 天+ 未修改: S3 Glacier Instant Retrieval ($0.004/GB/month, 节省 83%)

$$
\text{Without tiering: } 35\text{PB} \times \$0.023 = \$805K/\text{month}
$$

$$
\text{With tiering: } 5\text{PB} \times \$0.023 + 10\text{PB} \times \$0.0125 + 20\text{PB} \times \$0.004
$$

$$
= \$115K + \$125K + \$80K = \$320K/\text{month (节省 60%)}
$$

### 10x / 100x 规模变化 (Scale Evolution)

**10x (50 亿用户, 10 亿 DAU)**:
- 元数据: MySQL 分片从 8 -> 80 shards，或迁移到 **TiDB / CockroachDB** (分布式 SQL)
- 存储: 350 PB，需要自建对象存储 (参考 Dropbox **Magic Pocket**，
  从 S3 迁移到自建存储，节省 50%+ 成本)
- 通知: WebSocket 5 亿连接，需要自建推送基础设施

**100x**:
- 需要自建 CDN 和骨干网络
- 元数据层需要完全自研的分布式数据库
- 需要跨大陆的多活 (Active-Active) 架构 + 全局冲突解决
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Follow-up Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

### Q1: 如果一个用户有 100 万个小文件 (比如代码仓库), 打开文件夹会很慢, 怎么优化?

**承认挑战**: 100 万文件 x 500 字节元数据 = 500 MB 元数据，全量加载到客户端
不现实。传统的 `ls` 式列表在 > 10K 文件时用户体验恶化。

**缓解措施**:
1. **分页加载 (Pagination)**: 文件夹内容按修改时间倒序分页，
   每次只加载 100 条。用户滚动时懒加载
2. **元数据增量同步**: 客户端只拉取上次同步后变更的文件元数据 (基于 cursor)，
   不拉取全量。首次同步用 snapshot + incremental 的方式:
   先下载 compressed snapshot，然后增量追赶
3. **本地索引**: 客户端 SQLite 建立完整的文件索引，
   文件夹浏览直接查本地 DB (毫秒级)，后台异步同步
4. **服务端缓存**: Redis 缓存高频访问文件夹的元数据列表，TTL 5 分钟

**数据支撑**: Dropbox 对 > 50 万文件的用户使用 "Smart Sync" --
文件在本地只显示占位符 (placeholder)，内容在首次打开时按需下载。

### Q2: 如果用户在飞机上离线编辑了 50 个文件, 重新联网后如何同步?

**承认复杂性**: 离线期间可能累积大量修改，且其他设备也可能修改了相同文件。

**缓解措施**:
1. **本地变更队列 (Local Change Queue)**: 客户端在 SQLite 中记录所有离线修改
   (文件路径、修改时间、chunk hash 变化)，按时间顺序排列
2. **重新上线同步流程**:
   a. **拉取服务端变更**: 用离线前的 cursor 拉取所有未同步的服务端变更
   b. **冲突检测**: 对每个本地修改的文件，检查服务端是否也有该文件的新版本
   c. **无冲突文件**: 直接上传 (占大多数，> 99%)
   d. **冲突文件**: 创建冲突副本，保留两个版本
3. **优先级排序**: 最近修改的文件优先同步 (用户最关心最近编辑的内容)
4. **带宽控制**: 50 个文件一次性上传可能占用大量带宽，
   使用速率限制 (如最多 4 个并行 chunk 上传) 避免影响其他网络活动

**实际效果**: 50 个文件 x 平均 500 KB x 10% 变更 = 2.5 MB 实际传输量
(Delta Sync 效果)。在正常网络下 < 5 秒完成。

### Q3: Chunk 去重索引 (100 亿条记录) 如何高效存储和查询?

**规模**: 1000 亿文件 / 平均 4 MB chunk size = ~2.5 万亿 chunks?
不对 -- 平均文件 500 KB < 4 MB，大多数文件只有 1 个 chunk。
实际: ~1000 亿 chunks (去重前) -> 去重后 ~600 亿 unique chunks。

**方案: 两级索引**:
1. **L1: Redis Bloom Filter**: 所有 chunk hash 的 Bloom Filter，
   快速判断 "definitely not exists" (假阳率 < 1%)
   - 内存: 600 亿 x 10 bits = ~75 GB (可分布在 10 个 Redis 节点)
2. **L2: Redis Hash (热数据)**: 最近 30 天上传的 chunk hash -> S3 key
   - 约 20 亿条，每条 100 bytes = 200 GB
3. **L3: Cassandra (全量)**: 600 亿条 chunk hash -> S3 key
   - Cassandra 分布式存储，按 hash 前缀分区

**查询流程**:
1. 查 Bloom Filter -> 不存在 -> 需要上传 (快速路径, < 1ms)
2. 存在 -> 查 Redis L2 -> 命中 -> 秒传 (P99 < 5ms)
3. Redis L2 未命中 -> 查 Cassandra L3 -> 命中 -> 秒传 (P99 < 20ms)
4. Cassandra 未命中 -> Bloom Filter 假阳性 -> 正常上传

### Q4: 如果某个热门分享文件被 100 万人同时下载, 怎么处理?

**场景**: 一个公开分享的 100 MB 文件，100 万并发下载。

**缓解措施**:
1. **CDN 缓存**: 文件 chunk 已在 CDN 边缘节点缓存。
   100 万请求大多由 CDN 直接响应，不回源
2. **预热 (Pre-warm)**: 当分享链接访问量在 10 分钟内超过 1000 次，
   自动将 chunk 推送到全球 TOP 50 CDN 节点
3. **限流与公平排队**: 对单个分享链接设置下载并发上限
   (如 10K 并发)，超出的请求排队等待
4. **带宽计费保护**: 免费用户的分享链接每月限制 20 GB 传输量,
   超出后降速或要求升级

**回源风暴保护**:
- CDN Shield 层做 **Request Coalescing (请求合并)**:
  100 个边缘节点同时缓存未命中 -> Shield 只向 S3 发 1 个请求
- S3 的读取 QPS 上限是 5,500/s per prefix,
  使用随机 prefix 分散热点: `chunks/{random_prefix}/{chunk_hash}`

### Q5: 版本历史保留 30 天, 存储成本怎么控制?

**问题**: 频繁修改的文件可能产生大量版本。比如一个开发者每天保存代码文件
100 次，30 天 = 3000 个版本。

**缓解措施**:
1. **版本合并 (Version Compaction)**: 不保留每次保存的完整版本,
   而是:
   - 最近 1 小时: 保留每次保存 (完整粒度)
   - 1 小时 - 24 小时: 每 10 分钟保留一个版本 (合并间隔内的变更)
   - 1 天 - 7 天: 每小时保留一个版本
   - 7 天 - 30 天: 每天保留一个版本
   - 类似 Time Machine / ZFS snapshot 策略
2. **增量存储 (Incremental Storage)**: 版本之间只存 chunk 差异,
   不存完整文件。相邻版本共享未变更的 chunk (通过 ref_count)
3. **版本清理任务**: 后台 job 每天运行，根据上述策略合并/删除过期版本，
   回收 chunk (ref_count 降为 0 时删除 S3 对象)

**成本效果**: 原始 750 TB/月版本存储 -> 合并后约 100 TB/月,
节省 87%。加上 S3 Glacier 冷存储进一步降低成本。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1-Hour Interview Pacing Guide)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 面试节奏指南 (1-Hour Interview Pacing Guide)

### 3 分钟电梯演讲版 (Elevator Pitch)

"云存储的核心挑战是: 5 亿用户的 1000 亿文件, 要在任意设备上做到低延迟增量
同步, 同时保证零数据丢失。我的方案围绕三个核心设计:

1) **Block-level Delta Sync**: 客户端用 CDC (Rabin Fingerprint) 做内容定义分块,
   平均 4 MB/chunk。文件修改后只上传变更的 chunk, 带宽节省 90%+

2) **服务端去重**: SHA-256 chunk hash 查询去重索引 (Bloom Filter + Redis +
   Cassandra)。跨用户相同内容秒传, 节省 30-40% 存储

3) **冲突检测与解决**: 基于版本号乐观锁 + 冲突副本策略。多设备并发修改时
   创建冲突副本, 保证零数据丢失

架构: Sync Service 编排同步流程, S3 存 chunk, MySQL 存元数据 (user_id 分片),
Redis 做缓存和去重索引, WebSocket 做实时通知。

规模: 1 亿 DAU, 17K 峰值同步 QPS, 52K chunk QPS, 35 PB 存储 (去重后),
月成本 ~$1.5M。"

### 完整 1 小时面试节奏

#### 0-5 分钟: 需求澄清

**开场**: "云存储有三个核心维度需要权衡: 同步速度 vs 带宽成本, 一致性 vs
可用性, 以及存储成本 vs 版本保留。让我先确认几个关键问题。"

**必须澄清的问题**:
1. "是文件级同步 (Dropbox) 还是实时协同编辑 (Google Docs)?
   我假设文件级同步, 实时协编是另一个设计题"
2. "需要支持多大的单文件? 我按最大 50 GB 设计"
3. "是否需要端到端加密? 我先设计不加密版本, E2E 作为扩展讨论"
4. "用户文件量级? 我按每用户 200 文件, 5 亿用户估算"

**画出需求框架**:
```
FR: 上传/下载, 自动同步, 分享, 版本历史, 离线编辑
NFR: 17K sync QPS, sync < 500ms, 99.99% 可用, 11 个 9 持久性
```

#### 5-15 分钟: 高层架构

**画客户端 + 服务端架构**:

"客户端 (Write Path)":
```
File Watcher -> Chunker (CDC/Rabin) -> Delta Engine
  -> Sync Service: send chunk hashes -> dedup check
  -> Upload needed chunks via Presigned URL -> S3
  -> Commit version -> MySQL (atomic update)
  -> Kafka event -> Notification Service -> WebSocket to other devices
```

"客户端 (Read Path)":
```
WebSocket notification -> pull changes (cursor-based)
  -> diff remote vs local chunk lists
  -> download missing chunks from CDN/S3
  -> reassemble file locally
```

**逐层解释**:
- **为什么用 CDC 而不是固定分块?** "固定分块在文件头部插入时所有 chunk 偏移,
  CDC 用 Rabin Fingerprint 在内容边界切分, 中间插入只影响 1-2 个 chunk"
- **为什么客户端做 chunking?** "减少服务端计算负担, 而且客户端有完整的旧版本
  可以做本地 diff, 服务端只需要存储和去重"
- **为什么用 MySQL 而不是 NoSQL?** "文件系统是树形结构, 重命名文件夹需要
  原子更新所有子节点的路径, 需要事务支持"

**数据库选择**:
- "MySQL 存文件元数据 + 版本历史 (强一致, 事务), Redis 缓存热数据 + 去重索引,
  Cassandra 存冷 chunk 索引, S3 存文件内容, Kafka 做事件流"

#### 15-25 分钟: 深度剖析 -- Delta Sync

**核心挑战**: "如何最小化每次同步的传输量?"

**CDC 算法讲解**:
- "用 48 字节滑动窗口计算 Rabin Fingerprint"
- "当指纹低 22 位全为 0 时, 标记为 chunk 边界"
- "平均 chunk 4 MB, 范围 2-8 MB"
- "文件中间插入只影响插入点的 1-2 个 chunk"

**去重流程**:
- "客户端计算所有 chunk 的 SHA-256 hash"
- "发送 hash 列表到服务端"
- "服务端查 Bloom Filter (75 GB) -> Redis (200 GB) -> Cassandra"
- "只上传服务端没有的 chunk"

**数据**: "实测 10 MB Word 文档修改 1 段落: 只有 1 个 4 MB chunk 变化,
实际传输 ~4 MB 而不是 10 MB。Excel 文件更显著: 修改 1 个 cell,
传输 < 1 MB"

#### 25-35 分钟: 深度剖析 -- 冲突检测与解决

**场景**: "用户在笔记本和手机上同时编辑同一个文件"

**检测**: "每次提交带 parent_version。如果 current_version != parent_version,
说明有其他设备先一步修改了"

**解决**: "创建冲突副本: report (conflicted copy from MacBook 2024-01-15).pdf。
两个版本都保留, 用户手动选择。文本文件可以叠加三方合并"

**为什么不用 CRDT?** "CRDT 适合字符级实时协编 (Google Docs),
对二进制文件 (PDF, 图片) 无法自动合并。文件级同步用版本号 + 冲突副本更实际"

#### 35-45 分钟: 深度剖析 -- 存储与成本优化

**去重效果**:
- "跨用户去重: 同一个 npm package 被 100 万开发者同步, 只存 1 份"
- "节省 30-40% 存储: 50 PB -> 35 PB"

**分层存储**:
- "S3 Standard/IA/Glacier 三层, 存储成本从 $800K 降到 $320K/月"

**版本合并**:
- "最近 1 小时全保留, 之后逐渐降低粒度, 版本存储节省 87%"

#### 45-50 分钟: 权衡讨论

**3 个核心决策**:
1. "CDC vs 固定分块: CDC 多 5% CPU 开销, 但带宽节省 90%+, 值得"
2. "MySQL vs NoSQL: 牺牲水平扩展便利性, 换取树形结构的事务和一致性保证"
3. "冲突副本 vs LWW: 用户体验略差 (需要手动解决), 但保证零数据丢失"

**10x/100x**: "10x 需要从 S3 迁移到自建对象存储 (参考 Dropbox Magic Pocket);
100x 需要完全自研分布式文件系统 + 多活架构"

#### 50-55 分钟: 收尾

**我会改进什么**:
- 添加 **Smart Sync (智能同步)**: 大文件在本地只显示占位符,
  按需下载。节省客户端磁盘空间
- 实现 **端到端加密 (E2E Encryption)**: 客户端加密后上传,
  服务端只存密文。代价: 无法做服务端去重 (加密后 hash 不同)
- 添加 **LAN Sync (局域网同步)**: 同一局域网内的设备直接 P2P 同步,
  不经过云端。Dropbox 已有此功能, 大幅减少带宽消耗

**监控清单**:
- 同步延迟 (P50/P99)
- 冲突率
- Chunk 去重命中率
- S3 上传/下载成功率
- WebSocket 连接数与重连率

#### 55-60 分钟: 向面试官提问

- "你们的存储后端是自建还是用 S3? 什么规模下做了迁移?"
- "冲突解决策略是 LWW 还是冲突副本? 用户反馈如何?"
- "最大的运维挑战是什么? 是元数据规模还是存储成本?"

---

### 面试核心要点总结

关键设计决策:
- **CDC 分块 (Rabin Fingerprint)**: 内容边界切分, 中间插入只影响 1-2 个 chunk
- **三级去重索引**: Bloom Filter (75 GB) -> Redis (200 GB) -> Cassandra,
  chunk 级去重节省 30-40% 存储
- **Delta Sync**: 只传输变更 chunk, 带宽节省 90%+
- **冲突副本策略**: 多设备冲突时保留两个版本, 保证零数据丢失
- **WebSocket 实时通知**: 文件变更秒级推送到其他在线设备

规模: 1 亿 DAU, 1000 亿文件, 35 PB 存储, 17K 峰值同步 QPS,
52K chunk QPS, 856K 元数据 QPS, ~$1.5M/月。
"""


def populate_interview_cloud_storage() -> None:
    """Create or update the interview-cloud-storage record with all 8 sections."""
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
    populate_interview_cloud_storage()
