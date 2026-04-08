"""Populate interview-web-crawler system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design a Web Crawler --
URL frontier with priority queue, distributed crawling with consistent hashing,
Bloom filter deduplication, politeness enforcement (robots.txt + rate limiting),
content extraction & storage, and fault tolerance.
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

SLUG = "interview-web-crawler"
TITLE = "Design a Web Crawler"
DISPLAY_ORDER = 117

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个**分布式网络爬虫 (Distributed Web Crawler)**，能够从种子 URL 出发，
递归抓取整个互联网 (或指定域名集合) 的网页内容。爬虫需要高效地发现新 URL、
下载网页、提取内容和链接，并将数据存入后端存储供搜索引擎索引或数据分析使用。

核心挑战在于：(1) **规模** -- 互联网有数十亿网页，单机无法胜任；
(2) **去重** -- 避免重复抓取相同 URL 或相同内容，浪费带宽和存储；
(3) **礼貌性 (Politeness)** -- 遵守 `robots.txt` 和速率限制，不对目标网站
造成过大压力；(4) **容错** -- 爬虫长时间运行，必须能从节点故障中恢复而不丢失进度。

### 功能性需求 (Functional Requirements)

1. **种子 URL 管理 (Seed URL Management)**: 支持从一组种子 URL 出发，发现并
   递归抓取链接到的所有页面
2. **网页下载 (Page Fetching)**: HTTP/HTTPS 请求下载网页，处理重定向、超时、
   错误码 (4xx/5xx)
3. **内容提取 (Content Extraction)**: 从 HTML 中提取文本内容、元数据 (title,
   description) 和超链接
4. **URL 去重 (URL Deduplication)**: 确保同一 URL 不被重复抓取
5. **内容去重 (Content Deduplication)**: 检测不同 URL 指向的相同内容
   (镜像站、URL 别名)
6. **robots.txt 遵守**: 解析并缓存目标站点的 `robots.txt`，跳过禁止抓取的路径
7. **优先级调度 (Priority Scheduling)**: 根据页面重要性 (PageRank、更新频率、
   域名权重) 决定抓取顺序

### 非功能性需求 (Non-Functional Requirements)

- **可扩展性 (Scalability)**: 每天抓取 10 亿页面 (约 11,500 页/秒)，
  可水平扩展到数百台爬虫节点
- **吞吐量 (Throughput)**: 单节点 100-500 页/秒 (受网络带宽和目标站点
  响应速度限制)
- **延迟 (Latency)**: 无严格延迟要求，但新发现的高优先级 URL 应在分钟级
  内被调度抓取
- **可用性 (Availability)**: 99.9% -- 允许短暂停机，但不应丢失已发现的 URL 队列
- **持久性 (Durability)**: 已抓取内容零丢失；URL Frontier 持久化，节点重启
  后可恢复进度
- **礼貌性 (Politeness)**: 同一域名的请求间隔不低于该站点
  `Crawl-delay` 指定值 (默认 1 秒)

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 爬取范围是整个互联网还是特定域名集合?**
   -- WHY: 全网爬取需要处理数十亿 URL 的去重和优先级排序；特定域名集合
   可以用更简单的队列结构

2. **Q: 是否需要渲染 JavaScript (headless browser)?**
   -- WHY: 大量现代网站使用 SPA (Single Page Application) 框架，
   纯 HTTP GET 只能拿到空壳 HTML；如果需要渲染 JS，爬取成本增加 10-50 倍

3. **Q: 是否需要增量抓取 (incremental crawl)?**
   -- WHY: 全量重爬 vs 只抓变化页面，决定了是否需要存储上次抓取的
   内容哈希 + `Last-Modified`/`ETag` 头信息

4. **Q: 存储抓取到的原始 HTML 还是提取后的结构化数据?**
   -- WHY: 原始 HTML 存储量是结构化数据的 5-10 倍；但保留原始 HTML
   允许后期重新解析

5. **Q: 是否需要处理媒体文件 (图片、视频、PDF)?**
   -- WHY: 媒体文件大小远超 HTML (平均 HTML 50KB vs 图片 200KB+)，
   显著影响带宽和存储估算

6. **Q: 抓取频率如何确定? 是一次性快照还是持续运行?**
   -- WHY: 持续运行需要 URL 刷新调度策略 (哪些页面需要更频繁重爬)，
   一次性快照只需一个简单的 BFS/DFS 队列

7. **Q: 如何处理 10K 台被黑机器的变种? (10K hacked machines variant)**
   -- WHY: 这是面试中常见的扩展问题 -- 10K 台机器组成的分布式爬虫如何
   协调工作分配? 答案是**分布式哈希映射 (Distributed Hash Map)**: 每台
   机器负责一组域名 (按域名哈希分配)，避免多台机器同时爬同一站点

### 不在范围内 (Out of Scope)

- 搜索引擎索引构建 (indexing) 和排序 (ranking) -- 只负责抓取
- 网页内容分析 (NLP、分类、情感分析)
- 反爬虫对抗 (CAPTCHA 绕过、IP 轮换) -- 只做合法合规抓取
- 用户界面 (爬虫管理后台)
"""

# ---------------------------------------------------------------------------
# S2: Architecture (High-Level Design -- 10 min)
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 高层架构 (High-Level Design)

### 核心服务与职责 (Core Services)

```
种子 URL (Seed URLs)
  |
  v
[URL Frontier] -- 优先级队列 + 域名队列
  |
  +---> [DNS Resolver Cache] -- DNS 预解析与缓存
  |
  v
[Fetcher Workers] (N 台) -- HTTP 下载，遵守 politeness
  |
  v
[Content Parser] -- HTML 解析，提取文本 + 链接
  |
  +---> [URL Filter & Normalizer] -- 去重、标准化
  |       |
  |       v
  |     [Bloom Filter / URL Seen DB] -- 已见 URL 集合
  |       |
  |       v (新 URL)
  |     [URL Frontier] (回环)
  |
  +---> [Content Dedup] -- SimHash/MinHash 内容指纹
  |
  v
[Content Store] -- 原始 HTML + 提取后内容
  |
  v
[Indexer / Analytics Pipeline] -- 下游消费者
```

### 组件详解 (Component Details)

**1. URL Frontier (URL 前沿队列)**

URL Frontier 是爬虫的"心脏"，负责 URL 的存储和调度。它有两层结构：

- **优先级队列 (Priority Queue)**: 前端多个桶 (bucket)，每个桶对应一个优先级。
  高优先级 URL (如新闻首页、高 PageRank 页面) 优先被调度。使用**加权轮询
  (Weighted Round-Robin)** 从各优先级桶中选取 URL。
- **域名队列 (Per-Host Queue)**: 后端按域名分组的 FIFO 队列。每个域名一个队列，
  确保同一域名的请求不会并行发出，遵守 `Crawl-delay`。

这种前端 (优先级) + 后端 (礼貌性) 的双层设计解耦了"爬什么"和"什么时候爬"。

**2. Fetcher Workers (抓取工作节点)**

- 分布式部署，每个 Worker 从 URL Frontier 领取一批 URL
- 使用**异步 HTTP 客户端** (如 `aiohttp`) 并发下载
- 维护每域名的**速率限制器 (Rate Limiter)**: 令牌桶 (Token Bucket) 算法
- 处理 HTTP 重定向 (最多 5 跳)、超时 (30s)、重试 (指数退避，最多 3 次)
- **robots.txt 缓存**: 每个域名的 robots.txt 缓存 24 小时，首次访问时同步拉取

**3. Content Parser (内容解析器)**

- 使用 DOM 解析器 (如 `lxml`, `BeautifulSoup`) 提取:
  - 页面文本内容 (去除 HTML 标签和脚本)
  - 元数据 (`<title>`, `<meta description>`, `<meta keywords>`)
  - 所有超链接 (`<a href="...">`) -- 绝对化后送回 URL Frontier
  - 结构化数据 (`<script type="application/ld+json">`)

**4. URL Filter & Normalizer (URL 过滤与标准化)**

标准化规则:
- 统一小写 scheme 和 host: `HTTP://Example.COM` -> `http://example.com`
- 移除默认端口: `http://example.com:80` -> `http://example.com`
- 移除 fragment: `http://example.com/page#section` -> `http://example.com/page`
- 排序 query 参数: `?b=2&a=1` -> `?a=1&b=2`
- 移除常见跟踪参数: `utm_source`, `utm_medium`, `fbclid`

过滤规则:
- 排除非 HTTP(S) 协议 (mailto:, javascript:, ftp:)
- 排除已知低价值后缀 (.css, .js, .ico, .woff)
- 排除超长 URL (>2048 字符)
- 排除无限爬取陷阱 (日历翻页、session ID 路径)

### 数据库选型与理由 (Database Choices)

| 存储 | 技术选择 | 理由 |
|------|----------|------|
| **URL Frontier** | **RocksDB** (嵌入式) + **Kafka** (分布式) | 本地 RocksDB 提供单节点高速持久化队列；Kafka 在节点间分发 URL |
| **已见 URL 集合** | **Bloom Filter** (内存) + **RocksDB** (持久化) | Bloom Filter 提供 O(1) 概率去重；RocksDB 备份精确集合供恢复 |
| **robots.txt 缓存** | **Redis** (TTL 24h) | 所有 Worker 共享的域名级缓存，避免重复请求 |
| **抓取内容** | **HDFS / S3** (原始 HTML) + **HBase / BigTable** (提取后数据) | 原始 HTML 写入对象存储 (廉价、高吞吐)；结构化数据写入列存储 (支持快速查询) |
| **URL 元数据** | **MySQL / PostgreSQL** | 小规模元数据: 域名配置、优先级权重、爬取统计 |
| **DNS 缓存** | **本地 LRU 缓存** + **Redis** | DNS 查询延迟约 10-50ms，缓存命中可降到 <1ms |

### 通信模式 (Communication Patterns)

- **拉模式 (Pull)**: Fetcher Worker 从 URL Frontier 拉取一批 URL (batch size 100-500)
- **推模式 (Push)**: Content Parser 将新发现的 URL 推入 Kafka topic
- **Kafka 消息**: URL 分发 (按域名哈希分区)、内容写入通知、抓取状态事件
- **gRPC**: Worker 之间的健康检查和负载均衡协调

### 数据分区策略 (Data Partitioning)

- **按域名哈希分区 (Shard by Domain Hash)**: 同一域名的所有 URL 路由到同一个
  Fetcher Worker，天然满足 politeness (单域名串行)
- 使用**一致性哈希 (Consistent Hashing)** 分配域名到 Worker，支持节点动态
  增减而不需要全量重分配
- 热门域名 (如 wikipedia.org) 可能成为热点 -- 通过**虚拟节点 (Virtual Nodes)**
  将其分散到多个 Worker (但仍需协调速率限制)
"""

# ---------------------------------------------------------------------------
# S3: Dataflow (API Design + Data Flow -- 5 min)
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### 内部 API 端点 (Internal API Endpoints)

爬虫系统主要是内部系统，API 用于管理和监控:

**爬虫管理:**
```
POST /api/v1/crawl/seeds
     Body: { urls: ["https://example.com", ...], priority: "high" }
     -> 202: { job_id, urls_accepted: 150, urls_rejected: 2 }

GET  /api/v1/crawl/status
     -> 200: { active_workers: 48, urls_in_frontier: 12_500_000,
               pages_crawled_today: 850_000_000, avg_fetch_rate: 9800/s }

POST /api/v1/crawl/pause
     Body: { domain: "example.com", duration_minutes: 60 }
     -> 200: { paused_until: "2026-04-08T12:00:00Z" }

GET  /api/v1/crawl/domain/{domain}/stats
     -> 200: { pages_crawled: 45000, last_crawled: "...",
               avg_response_time_ms: 230, robots_txt_cached: true }
```

**URL Frontier 管理:**
```
GET  /api/v1/frontier/size
     -> 200: { total: 12_500_000, by_priority: { high: 500_000,
               normal: 10_000_000, low: 2_000_000 } }

POST /api/v1/frontier/reprioritize
     Body: { domain: "news.example.com", new_priority: "high" }
     -> 200: { urls_affected: 3200 }
```

### 核心数据模型 (Core Data Models)

```
-- URL 记录 (URL Frontier 中的条目)
URL_Record {
    url_hash        CHAR(64) PRIMARY KEY,  -- SHA-256 of normalized URL
    original_url    TEXT NOT NULL,
    domain          VARCHAR(255) NOT NULL,
    priority        TINYINT DEFAULT 5,     -- 1 (highest) to 10 (lowest)
    status          ENUM('pending', 'fetching', 'done', 'failed', 'skipped'),
    depth           INT DEFAULT 0,         -- BFS depth from seed
    discovered_at   TIMESTAMP,
    last_fetched_at TIMESTAMP,
    fetch_count     INT DEFAULT 0,
    next_fetch_at   TIMESTAMP,             -- for incremental crawl
    http_status     SMALLINT,
    content_hash    CHAR(64),              -- for content dedup
    parent_url_hash CHAR(64)               -- which page linked here
}
INDEX idx_domain_status ON URL_Record(domain, status)
INDEX idx_priority_next ON URL_Record(priority, next_fetch_at)

-- 页面内容 (Content Store)
Page_Content {
    url_hash        CHAR(64) PRIMARY KEY,
    raw_html        BLOB,                  -- compressed (gzip)
    extracted_text  TEXT,
    title           VARCHAR(500),
    meta_desc       VARCHAR(1000),
    outgoing_links  JSON,                  -- ["https://...", ...]
    content_hash    CHAR(64),              -- SimHash fingerprint
    fetch_timestamp TIMESTAMP,
    http_headers    JSON,
    content_type    VARCHAR(100),
    content_length  INT
}

-- 域名配置 (Per-Domain Settings)
Domain_Config {
    domain          VARCHAR(255) PRIMARY KEY,
    robots_txt      TEXT,
    robots_fetched  TIMESTAMP,
    crawl_delay_ms  INT DEFAULT 1000,
    max_concurrent  INT DEFAULT 1,
    priority_boost  FLOAT DEFAULT 1.0,
    last_crawled    TIMESTAMP,
    total_pages     INT DEFAULT 0,
    is_paused       BOOLEAN DEFAULT FALSE
}
```

### 读路径: 检查 URL 是否已抓取 (Read Path)

```
1. 新发现 URL -> URL Normalizer 标准化
2. 计算 SHA-256 哈希
3. 查询 Bloom Filter (内存): 如果返回"不存在" -> 肯定是新 URL -> 加入 Frontier
4. 如果 Bloom Filter 返回"可能存在" -> 查询 RocksDB 精确验证
5. 如果 RocksDB 确认存在 -> 检查是否需要刷新 (next_fetch_at < now)
6. 不需要刷新 -> 丢弃; 需要刷新 -> 更新优先级后重新入队
```

### 写路径: 抓取一个页面 (Write Path)

```
1. Fetcher Worker 从 URL Frontier 拉取一批 URL (按域名分组)
2. 检查域名 robots.txt (Redis 缓存 -> 如无则先抓取 robots.txt)
3. 检查 Crawl-delay: 距离上次请求该域名是否超过间隔?
   - 否 -> 放回队列，取下一个域名的 URL
   - 是 -> 继续
4. 发送 HTTP GET 请求 (带 User-Agent, Accept-Encoding: gzip)
5. 处理响应:
   - 2xx: 下载成功 -> Content Parser
   - 3xx: 提取 Location header, 新 URL 入队 (depth+1)
   - 4xx: 标记为 failed (404 = skipped)
   - 5xx: 指数退避重试，最多 3 次后标记 failed
   - Timeout: 重试一次，仍超时则标记 failed
6. Content Parser 提取文本 + 链接
7. 计算内容 SimHash 指纹 -> 与已有内容比对去重
8. 存储: 原始 HTML -> S3/HDFS; 提取数据 -> HBase
9. 新发现的链接 -> URL Normalizer -> Bloom Filter 去重 -> URL Frontier
10. 更新 URL_Record: status=done, last_fetched_at=now, content_hash
11. 通过 Kafka 发布抓取完成事件 -> 下游索引管道
```

### 异步路径 (Async Paths)

- **URL 分发 (Kafka)**: Content Parser 发现的新 URL 写入 Kafka topic
  (按域名哈希分区)，对应 Frontier 节点消费并入队
- **内容写入 (Kafka)**: 抓取到的内容通过 Kafka 异步写入 S3/HBase，
  与抓取主循环解耦
- **统计聚合 (Kafka Streams)**: 实时计算每域名 QPS、错误率、
  平均响应时间等监控指标
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Capacity Estimation + Core Algorithms -- 5 min)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### 基础假设 (Assumptions)

- 目标: 每月抓取 **150 亿页面** (15 billion pages/month)
- 平均页面大小: 原始 HTML 约 **100 KB** (压缩后约 20 KB)
- 提取后文本: 约 **10 KB/页**
- 平均每页包含 **50 个超链接**
- 爬取周期: 30 天连续运行
- URL 平均长度: **100 字节**
- 已知 URL 总量 (去重后): **100 亿** (10 billion)

### QPS 估算 (QPS Estimation)

$$
\text{Pages per second} = \frac{15 \times 10^9}{30 \times 24 \times 3600} \approx 5{,}787 \text{ pages/s}
$$

考虑 **3x 峰值系数 (Peak Factor)**:

$$
\text{Peak QPS} \approx 5{,}787 \times 3 = 17{,}361 \text{ pages/s}
$$

假设每页产生 **50 个新 URL**，URL 发现速率:

$$
\text{URL Discovery Rate} = 5{,}787 \times 50 = 289{,}350 \text{ URLs/s}
$$

经过去重后 (假设 10% 是新 URL):

$$
\text{New URL Rate} = 289{,}350 \times 0.1 = 28{,}935 \text{ URLs/s}
$$

### 存储估算 (Storage Estimation)

**原始 HTML (压缩后):**

$$
\text{Storage}_{\text{HTML}} = 15 \times 10^9 \times 20 \text{ KB} = 300 \text{ TB/month}
$$

**提取后文本:**

$$
\text{Storage}_{\text{text}} = 15 \times 10^9 \times 10 \text{ KB} = 150 \text{ TB/month}
$$

**URL 元数据:**

$$
\text{Storage}_{\text{URL}} = 10 \times 10^9 \times 200 \text{ bytes} = 2 \text{ TB}
$$

(每条 URL 记录约 200 字节: url_hash + domain + priority + timestamps + status)

### 带宽估算 (Bandwidth Estimation)

$$
\text{Bandwidth}_{\text{download}} = 5{,}787 \times 100 \text{ KB} = 579 \text{ MB/s} \approx 4.6 \text{ Gbps}
$$

峰值:

$$
\text{Peak Bandwidth} \approx 4.6 \times 3 = 13.8 \text{ Gbps}
$$

### 内存估算 (Memory Estimation)

**Bloom Filter 去重:**

对于 $n = 10 \times 10^9$ 个 URL，误判率 $p = 1\%$:

$$
m = -\frac{n \ln p}{(\ln 2)^2} = -\frac{10^{10} \times \ln 0.01}{0.4805} \approx 9.58 \times 10^{10} \text{ bits} \approx 11.2 \text{ GB}
$$

最优哈希函数个数:

$$
k = \frac{m}{n} \ln 2 = \frac{9.58}{1} \times 0.693 \approx 7
$$

即使用 **7 个哈希函数**，**11.2 GB 内存** 即可对 100 亿 URL 进行概率去重，
误判率仅 1%。这是 Bloom Filter 的核心优势 -- 相比存储完整 URL (2 TB)，
内存节省 **99.4%**。

**DNS 缓存:**

$$
\text{DNS Cache} = 10 \times 10^6 \text{ domains} \times 200 \text{ bytes} = 2 \text{ GB}
$$

**robots.txt 缓存:**

$$
\text{robots.txt Cache} = 10 \times 10^6 \text{ domains} \times 2 \text{ KB} = 20 \text{ GB}
$$

### 服务器估算 (Server Estimation)

假设单台爬虫节点 500 页/秒 (受限于网络带宽和目标站点响应):

$$
\text{Crawler Nodes} = \frac{17{,}361}{500} \approx 35 \text{ nodes (peak)}
$$

加上冗余和非抓取节点:

$$
\text{Total Nodes} \approx 35 \times 1.5 + 10 = 63 \text{ nodes}
$$

(10 个额外节点: URL Frontier 服务 x3, Content Store x3, DNS/robots 缓存 x2,
监控/协调 x2)

### 核心算法: SimHash 内容去重 (SimHash Content Dedup)

**SimHash** 用于检测**近似重复 (Near-Duplicate)** 页面。步骤:

1. 将文档分词 (tokenize) 为特征集合
2. 每个特征计算传统哈希 (如 MD5) 得到 64-bit 指纹
3. 用特征权重 (TF-IDF) 加权合并所有哈希:
   - 对每个 bit 位: 如果该 bit = 1 则加权重，否则减权重
4. 最终向量: 每个 bit 取符号 (正 -> 1, 负 -> 0) 得到 64-bit SimHash

$$
\text{SimHash}(D) = \text{sign}\left(\sum_{f \in D} w_f \cdot h(f)\right)
$$

其中 $w_f$ 是特征 $f$ 的权重，$h(f)$ 是 $f$ 的哈希值 (bit=1 -> +1, bit=0 -> -1)。

两个文档的 SimHash **汉明距离 (Hamming Distance)** 越小，内容越相似:

$$
\text{distance}(A, B) = \text{popcount}(\text{SimHash}(A) \oplus \text{SimHash}(B))
$$

阈值: 汉明距离 $\leq 3$ (64-bit) 认为是近似重复，跳过存储。

### 核心算法: Consistent Hashing (一致性哈希)

将 URL 的域名哈希到环上 ($[0, 2^{32})$)，每个 Crawler Node 也映射到环上。
URL 被分配给环上顺时针方向最近的节点。

$$
\text{node}(url) = \min_{n \in \text{Nodes}} \{ n \mid \text{hash}(n) \geq \text{hash}(\text{domain}(url)) \}
$$

**虚拟节点 (Virtual Nodes)**: 每个物理节点映射 $V$ 个虚拟节点到环上，
使负载更均匀。$V$ 通常取 100-200。节点增减时，只有 $\frac{1}{N}$ 的键需要
重新映射 (其中 $N$ 是节点数)。

### 汇总表 (Summary)

| 指标 | 数值 |
|------|------|
| 日均抓取 | 5 亿页 |
| 平均 QPS | ~5,800 页/秒 |
| 峰值 QPS | ~17,400 页/秒 |
| 下载带宽 | ~4.6 Gbps (峰值 13.8 Gbps) |
| 原始存储 (月) | 300 TB (压缩后) |
| Bloom Filter 内存 | 11.2 GB (100 亿 URL, 1% 误判率) |
| 爬虫节点数 | ~35 台 (峰值) + ~28 台辅助 |
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Deep Dive -- Scale & Reliability)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 深度剖析: 规模与可靠性 (Deep Dive: Scale & Reliability)

### 具体规模数字 (Concrete Scale Numbers)

| 指标 | 数值 |
|------|------|
| 已知 URL 总量 | 100 亿 |
| 月抓取量 | 150 亿页 |
| 并发爬虫节点 | 35-63 台 |
| URL Frontier 大小 | 5000 万 - 5 亿条 (活跃队列) |
| 每秒 URL 去重查询 | ~29 万次 |
| 存储增长速率 | ~10 TB/天 (压缩后) |

### 单点故障分析 (Single Point of Failure Analysis)

| 组件 | 故障影响 | 缓解策略 |
|------|----------|----------|
| **URL Frontier** | 爬虫无 URL 可抓 -- 全面停止 | 分布式 Frontier: 按域名分片到 3+ 节点，每节点有本地 RocksDB 持久化 |
| **Bloom Filter** | URL 去重失效 -- 大量重复抓取 | 定期快照到磁盘; 故障时从 RocksDB URL 集合重建 (约 30 分钟) |
| **DNS Cache (Redis)** | DNS 查询延迟暴增 | 本地 LRU 缓存兜底; Redis Sentinel 高可用 |
| **Kafka** | URL 分发中断 | 3 副本 (replication factor=3); 多 broker 部署 |
| **Content Store (S3/HDFS)** | 内容无法持久化 | S3 自带 11 个 9 持久性; HDFS 3 副本 |
| **协调服务 (ZooKeeper)** | 节点无法发现彼此 | 3 或 5 节点 ZooKeeper 集群; 本地缓存上次配置兜底 |

### 多数据中心 / 跨区域考虑 (Multi-Datacenter Considerations)

**地理分布式爬取策略:**

- **按地理位置分配域名**: 美国域名 (.com, .us) 由美国数据中心爬取，
  欧洲域名 (.eu, .de, .fr) 由欧洲数据中心爬取，亚洲域名 (.cn, .jp) 由
  亚洲数据中心爬取
- **优势**: 降低网络延迟 (本地爬取延迟 20-50ms vs 跨洋 200-300ms)，
  减少跨洋带宽费用
- **数据汇聚**: 各区域爬取的内容通过**异步复制**汇聚到中央数据湖 (S3)
  供全球索引使用

**Active-Active 模式:**
- 每个区域独立运行完整的爬虫集群
- URL Frontier 按域名地理位置分配 (不是按 consistent hashing)
- 跨区域 URL 去重: 各区域定期交换 Bloom Filter 快照
- 冲突解决: Last-Write-Wins -- 如果两个区域意外爬了同一页面，
  保留最新的抓取结果

**容灾:**
- 单区域故障: 该区域的域名自动转移到其他区域 (通过更新 Frontier 分配表)
- DNS 级路由: 无 (爬虫是主动出站，不是被动接收流量)

### 高并发处理 (High Concurrency Handling)

**连接池 (Connection Pooling):**
- 每个 Fetcher Worker 维护 **HTTP 连接池**，按域名复用 TCP 连接
- 连接池大小: 每域名 1-2 连接 (受 politeness 限制)，总连接数上限 1000/Worker
- 使用 HTTP/2 多路复用 (multiplexing) 减少连接数

**速率限制 (Rate Limiting):**
- **域名级令牌桶 (Per-Domain Token Bucket)**: 每个域名一个桶，
  令牌生成速率 = 1/Crawl-delay (默认 1 个/秒)
- **全局速率限制**: 出站总带宽不超过机房上行带宽的 80%
- 实现: Redis + Lua 脚本实现分布式令牌桶 (跨 Worker 共享域名速率限制)

**背压机制 (Backpressure):**
- 如果 Content Store 写入延迟增加 -> Fetcher 自动降低抓取速率
- URL Frontier 队列深度超过阈值 -> 暂停接受新 URL 直到队列消化

**优雅降级 (Graceful Degradation):**
- 大规模目标站点宕机: 自动检测连续 5xx 错误 -> 暂停该域名 1 小时
- Bloom Filter 内存压力: 降低误判率要求 (从 1% 放宽到 5%)，
  减少内存使用 40%
- 存储写入慢: 切换为只存提取后文本，暂不存原始 HTML

### 监控与告警 (Monitoring & Alerting)

**关键指标:**

| 指标 | 告警阈值 | 含义 |
|------|----------|------|
| `crawl_qps` | < 3000 (持续 5min) | 抓取吞吐量异常下降 |
| `frontier_size` | > 10 亿 或 < 100 万 | URL 积压过多或即将耗尽 |
| `bloom_filter_fpr` | > 5% | 误判率过高，可能导致大量漏抓 |
| `fetch_error_rate` | > 20% (持续 10min) | 网络问题或目标站点大面积宕机 |
| `dns_cache_miss_rate` | > 30% | DNS 缓存失效，延迟增加 |
| `content_store_lag` | > 10 min | 存储写入积压 |
| `worker_heartbeat_miss` | > 2 个节点 (1min) | 爬虫节点可能宕机 |
| `duplicate_crawl_rate` | > 5% | 去重机制失效 |
"""

# ---------------------------------------------------------------------------
# S6: Tradeoffs (Trade-off Discussion -- 10 min)
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡讨论 (Trade-off Discussion)

### 关键设计决策 (Key Design Decisions)

| 决策 | 方案 A | 方案 B | 我们的选择与理由 |
|------|--------|--------|-----------------|
| **URL 去重** | **Bloom Filter** (概率, 11.2 GB) | **HashSet / DB 精确查询** (100% 准确, 2 TB) | **Bloom Filter + RocksDB 二级验证**。11 GB 内存 vs 2 TB 磁盘，速度差 100 倍。1% 误判只导致少量漏抓，可接受 |
| **URL 分配策略** | **一致性哈希 (Consistent Hashing)** 按域名分配 | **中央调度器 (Central Scheduler)** 按负载分配 | **一致性哈希**。去中心化，无单点瓶颈; 天然保证同域名请求串行 (politeness); 节点增减平滑。中央调度器在 29 万 URL/秒下会成为瓶颈 |
| **内容去重** | **SimHash** (近似去重, 64-bit 指纹) | **MD5/SHA-256 精确哈希** (完全相同才去重) | **SimHash**。大量网页只有页眉页脚不同但主体内容相同 (模板化网站)，MD5 会认为它们是不同页面。SimHash 汉明距离 3 以内即判定重复，去重率高 30%+ |
| **页面存储格式** | **存原始 HTML** (100 KB/页) | **只存提取后文本** (10 KB/页) | **两者都存**。原始 HTML 允许后期重新解析 (提取算法升级时无需重爬); 提取后文本供索引直接使用。存储成本多 10x 但省去了重爬成本 |
| **Frontier 持久化** | **纯内存队列** (快, 但节点宕机丢数据) | **RocksDB 持久化队列** (稍慢, 但可恢复) | **RocksDB**。爬虫运行数天甚至数周，节点宕机概率非零; 丢失 Frontier 意味着丢失所有待爬 URL。RocksDB 的写入延迟 (<1ms) 对于爬虫的秒级调度周期可忽略 |

### CAP 定理应用 (CAP Theorem Application)

爬虫系统对**一致性**的要求较低:
- URL 去重允许**最终一致 (Eventual Consistency)**: 短暂的重复抓取 (几秒内)
  可以接受，不会造成严重后果
- 选择 **AP (可用性 + 分区容忍)**:  网络分区时各子集继续独立爬取，
  分区恢复后合并 Bloom Filter 即可

### 成本 vs 性能 (Cost vs Performance)

- **带宽是主要成本**: 13.8 Gbps 峰值带宽，按云服务商定价约 $0.05/GB，
  月费用约 $45,000
- 优化: (1) 请求 `Accept-Encoding: gzip` 减少传输量 60-80%;
  (2) 增量抓取 (`If-Modified-Since`, `ETag`) 避免重复下载未变化页面
- **存储是次要成本**: S3 存储 300 TB/月约 $6,900/月; 但随时间累积

### 复杂性 vs 简洁性 (Complexity vs Simplicity)

- Bloom Filter + SimHash + Consistent Hashing 增加了系统复杂度
- 但在 100 亿 URL 规模下，简单方案 (MySQL + 精确查询 + 中央调度)
  根本无法支撑
- **规模是复杂度的正当理由**: 这些算法和数据结构存在的原因正是为了
  解决简单方案无法处理的规模问题

### 10x / 100x 规模变化 (Scale Changes)

**10x (1500 亿页/月):**
- Bloom Filter 内存 -> 112 GB，需要分布式 Bloom Filter (每节点存部分)
- 爬虫节点 350+ 台，URL Frontier 需要分片到 30+ 台服务器
- 带宽 138 Gbps -- 需要多数据中心分散出站流量
- 存储 3 PB/月 -- 需要数据生命周期管理 (6 个月后归档到冷存储)

**100x (1.5 万亿页/月):**
- 已接近整个互联网规模 (约 500 亿可索引页面)
- 需要专用网络基础设施 (自有机房 + peering 协议降低带宽成本)
- Bloom Filter 不够用 -> 切换到**分布式哈希表 (DHT)** (如 Chord/Kademlia)
  实现精确去重
- 存储 30 PB/月 -> 需要自建存储集群 (Ceph/HDFS) 而非云服务
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Follow-up Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

### Q1: 如果一个爬虫节点宕机了怎么办? (Failure Scenario)

**承认局限**: 节点宕机时，该节点负责的域名会暂时无人爬取，Frontier 中
分配给该节点的 URL 无法被处理。

**缓解策略**:

1. **心跳检测 + 自动重分配**: 协调服务 (ZooKeeper) 检测节点心跳丢失
   (默认 30 秒超时)，触发一致性哈希环的节点移除，该节点的域名自动
   分配给相邻节点
2. **Frontier 持久化**: 每个节点的 RocksDB 队列持久化到本地磁盘，
   节点重启后可恢复; 如果是物理机故障，从 Kafka 消费位点重放最近
   未确认的 URL
3. **幂等抓取**: 即使部分 URL 被重复分配 (节点交接期间)，抓取操作
   本身是幂等的 -- 重复抓取只浪费一点带宽，不会产生错误数据
4. **恢复时间**: 心跳超时 30s + 重分配 10s + 新节点预热 60s = **约 2 分钟**

### Q2: 流量突然增长 10 倍怎么办? (Scale Challenge)

**承认局限**: 10x 流量意味着需要 350+ 爬虫节点，带宽 138 Gbps，
单个 Bloom Filter 需要 112 GB 内存 -- 超出单机容量。

**缓解策略**:

1. **水平扩展 (Auto-scaling)**: 爬虫节点无状态 (Frontier 在独立服务)，
   可以快速弹性扩展。在 Kubernetes 上根据 Frontier 队列深度触发 HPA
2. **分布式 Bloom Filter**: 将 Bloom Filter 按域名哈希分片到多台机器，
   每台只维护部分 URL 集合。查询时路由到对应分片 (与 URL 分配策略一致)
3. **多区域部署**: 将负载按地理区域分散，每个区域独立的 Frontier +
   Bloom Filter + 爬虫集群
4. **优先级降级**: 10x 规模时暂时只爬高优先级 URL (top 10% 的域名
   贡献 90% 的有价值内容)，低优先级 URL 延后
5. **预案**: 提前准备好 Terraform/CDK 模板，一键部署额外集群

### Q3: 两个 Worker 同时抓取同一个 URL 怎么办? (Data Consistency)

**承认局限**: 在分布式系统中，尤其是节点交接期间 (一致性哈希重映射)，
同一 URL 可能被分配给两个 Worker。

**缓解策略**:

1. **实际影响很小**: 重复抓取同一页面的后果只是浪费一次 HTTP 请求和
   少量带宽，不会产生数据不一致 (content_hash 相同，最终存储结果一致)
2. **乐观去重**: Content Store 写入时以 url_hash 为主键，重复写入
   是幂等的 (覆盖而非追加)
3. **Frontier 层去重**: URL Frontier 入队时检查 status -- 如果已经
   是 `fetching` 或 `done`，拒绝入队
4. **分布式锁 (可选但不推荐)**: 可以用 Redis 分布式锁保证同一 URL
   全局唯一执行，但锁的开销 (每次 1-2ms) 在 30 万次/秒的吞吐量下
   会显著降低性能。对于爬虫场景，"偶尔重复 > 全局锁" 是正确的权衡

### Q4: 如何处理爬虫陷阱 (Spider Trap)? (Edge Case)

**承认局限**: 部分网站会生成无限 URL (如日历翻页、session ID 路径、
URL 参数排列组合)，导致爬虫陷入无限循环。

**缓解策略**:

1. **最大深度限制 (Max Depth)**: 从种子 URL 出发的 BFS 深度超过阈值
   (如 15 层) 自动停止
2. **URL 模式检测**: 如果同一域名的 URL 中某个路径模式重复出现
   (如 `/calendar/2026/01`, `/calendar/2026/02`, ... `/calendar/9999/12`)，
   自动识别并限制
3. **每域名页面上限**: 单个域名最多抓取 N 页 (如 100 万页)，超过后降低
   优先级或跳过
4. **URL 长度限制**: 超过 2048 字符的 URL 直接丢弃 (正常页面 URL
   很少超过 200 字符)
5. **人工黑名单**: 已知的爬虫陷阱域名加入黑名单

### Q5: Bloom Filter 误判导致漏抓了重要页面怎么办? (Algorithm Limitation)

**承认局限**: Bloom Filter 的 1% 误判率意味着每 100 个新 URL 中有 1 个
被错误地认为"已抓取"而跳过。对于 100 亿 URL 中的 1 亿条漏抓 -- 数量不小。

**缓解策略**:

1. **降低误判率**: 增加 Bloom Filter 内存到 22.4 GB (翻倍)，
   误判率降到 0.01% (百万分之一百)
2. **高优先级 URL 精确验证**: 对优先级 >= 8 (top 20%) 的 URL，
   Bloom Filter 检查后追加一次 RocksDB 精确查询，确保高价值页面不被漏抓
3. **定期全量重爬**: 每 3-6 个月对已知的高价值域名进行全量重爬，
   不依赖 Bloom Filter 去重 (直接从域名站点地图 sitemap.xml 获取 URL 列表)
4. **Counting Bloom Filter 变体**: 支持删除操作，可以在 URL 被更新后
   重新加入队列
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1-Hour Interview Pacing Guide)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 面试节奏指南 (1-Hour Interview Pacing Guide)

### 3 分钟电梯演讲版 (3-Minute Elevator Pitch)

> 我会设计一个**分布式网络爬虫**，核心是一个**双层 URL Frontier**:
> 前端按优先级排序决定"爬什么"，后端按域名分组保证"礼貌性"。
> 使用**一致性哈希**按域名将 URL 分配到爬虫节点，保证同域名请求串行。
> URL 去重用**Bloom Filter** (100 亿 URL 仅需 11 GB 内存)，内容去重用
> **SimHash** (汉明距离 <= 3 判定近似重复)。每个节点用 RocksDB 持久化
> 本地 Frontier 队列，Kafka 负责跨节点 URL 分发。整个系统按域名地理位置
> 进行多区域部署，降低延迟和带宽成本。

### 完整 1 小时面试节奏 (Full 1-Hour Pacing)

**0-5 分钟: 需求澄清 (Requirements Clarification)**

- 确认范围: 全网爬取还是特定域名? -> 假设全网
- 确认规模: 每天抓取多少页? -> 5 亿页/天 (约 6000 页/秒)
- 确认深度: 是否需要渲染 JavaScript? -> 假设不需要 (纯 HTTP GET)
- 确认存储: 存原始 HTML 还是提取后文本? -> 两者都存
- 列出 FR: 种子管理、页面下载、内容提取、URL 去重、robots.txt、优先级调度
- 列出 NFR: 可扩展到数百节点、每天 5 亿页、99.9% 可用性

**5-15 分钟: 高层架构 (High-Level Architecture)**

- 画出核心组件: Seed URLs -> URL Frontier -> Fetcher Workers ->
  Content Parser -> Content Store
- 讲解 URL Frontier 双层结构 (优先级 + 域名队列)
- 讲解数据库选型: RocksDB (Frontier), Bloom Filter (去重),
  S3/HDFS (内容存储), Redis (DNS/robots 缓存)
- 讲解一致性哈希: 域名 -> Worker 映射，虚拟节点

**15-40 分钟: 深度剖析 (Deep Dive -- 选 2-3 个最有趣的组件)**

**深度话题 1: URL Frontier 设计 (10 min)**
- 双层队列: 前端优先级桶 (加权轮询) + 后端域名 FIFO
- 为什么不用简单的 Priority Queue? -> 无法保证 politeness
- 为什么不用纯域名队列? -> 高优先级 URL 可能被低优先级的大站阻塞
- 持久化: RocksDB 写入 <1ms，节点宕机可恢复
- 与 Kafka 的集成: 新 URL 通过 Kafka topic (按域名分区) 路由到正确的 Frontier 节点

**深度话题 2: Bloom Filter 去重 (10 min)**
- 为什么不用 HashSet? 100 亿 URL x 200 bytes = 2 TB 内存，不现实
- Bloom Filter: 100 亿 URL 仅需 11.2 GB，1% 误判率
- 公式推导: $m = -\frac{n \ln p}{(\ln 2)^2}$，$k = \frac{m}{n} \ln 2$
- 误判的影响: 漏抓少量页面 vs 节省 99.4% 内存 -- 值得
- 高优先级 URL 的二级精确验证 (RocksDB)
- Bloom Filter 快照与故障恢复

**深度话题 3: 一致性哈希 + Politeness (5 min)**
- 域名 -> 节点映射，同域名串行抓取
- 虚拟节点避免负载倾斜
- 节点故障: 域名自动迁移到相邻节点
- 热门域名处理: 多个虚拟节点 + 协调速率限制

**40-50 分钟: 权衡与扩展 (Trade-offs & Scaling)**

- Bloom Filter vs 精确去重: 内存 vs 准确率
- SimHash vs MD5: 近似去重 vs 精确去重
- AP vs CP: 爬虫选择可用性优先
- 10x 规模: 分布式 Bloom Filter + 多区域部署
- 100x 规模: 自建基础设施 + DHT 替换 Bloom Filter

**50-55 分钟: 总结与改进 (Wrap-up)**

- 如果时间更多我会改进:
  1. 增量抓取 (If-Modified-Since / ETag) 减少重复下载
  2. JavaScript 渲染支持 (headless browser 集群)
  3. 机器学习优先级预测 (根据页面更新频率自动调整重爬间隔)
  4. 更智能的爬虫陷阱检测 (URL 模式识别 + 内容相似度异常检测)
- 监控: crawl_qps, frontier_size, bloom_fpr, error_rate, duplicate_rate

**55-60 分钟: 向面试官提问**

- "贵公司的爬虫规模大概在什么量级? 是否已经在用类似的架构?"
- "对于 JavaScript 密集的网站，你们是如何处理的?"
- "URL 优先级的确定是用人工规则还是机器学习模型?"
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def populate_interview_web_crawler() -> None:
    """Insert or update the interview-web-crawler SystemDesign record."""
    init_db()
    db = SessionLocal()
    try:
        record = db.query(SystemDesign).filter_by(slug=SLUG).first()
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
    populate_interview_web_crawler()
