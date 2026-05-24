"""Backfill cheat_sheet column for interview SDs id=19..28 (batch 3 of T-P2-683).

Targets (display_order 110-119, all currently empty on cheat_sheet; id=23
price-drop-tracker was completed in 2026-05-01 fix and is excluded):
  id=19 interview-top-k-heavy-hitters
  id=20 interview-ad-click-aggregator
  id=21 interview-video-streaming
  id=22 interview-cloud-storage
  id=24 interview-online-judge
  id=25 interview-ticket-reservation
  id=26 interview-web-crawler
  id=27 interview-auction-system
  id=28 interview-distributed-cache

Idempotent: rewrites only the cheat_sheet column for the 9 target slugs;
all other columns are left untouched.

Style (per project memory feedback_content_style_cn_en + 2026-05-02 batch 1/2
reference seed_sd_cheat_sheets_ebay_20260502.py /
seed_sd_cheat_sheets_interview_batch2_20260502.py):
  - Markdown table with 11-12 rows.
  - Columns: 'Item' / 'Number / Decision'.
  - Chinese narration + English technical-term expansion on first use.
  - 250-700 chars (compact flash card).
  - Numbers / decisions sourced from each row's existing overview /
    production_constraints / tradeoffs / formulas columns -- no new content
    invented.

Part of T-P2-683 (batch 3 of ~3-4); final batch will handle the remaining
5 old Pinterest SDs (id=29..31, 33, 34).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

CHEAT_SHEETS: dict[str, str] = {
    "interview-top-k-heavy-hitters": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 1 亿 DAU, 50 亿事件/天, 5 亿不同 key |
| 峰值 QPS | 写 170K events/sec, Top-K 读 10K |
| 延迟 SLA | Top-K 查询 P99 <5ms |
| 计数算法 | **Count-Min Sketch** $w=2718, d=5$ = 54KB（vs HashMap 30GB） |
| 流式内存 | 总 ~25MB（CMS + Min-Heap, 64 分区 x 4 窗口） |
| Top-K 结构 | **Min-Heap** $O(\\log K)$（vs Sorted Array $O(K)$） |
| 流引擎 | **Apache Flink**（有状态窗口 + RocksDB checkpoint）vs Kafka Streams |
| 架构模式 | **Lambda**: 流式 CMS + 批处理每小时校准（vs Kappa 精度无保证） |
| 分区策略 | 按 **key 哈希**（同 key 同分区, 计数准确）vs 按时间 |
| 多 DC | 区域独立 + 异步全局合并（取 max count, 幂等且交换） |
| CAP 取向 | **AP**（大屏过时几秒可接受, 空白不可接受） |
| Kafka 容错 | 3 副本 + min.insync.replicas=2, Flink exactly-once |
""",

    "interview-ad-click-aggregator": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 5 亿 DAU, 100 亿展示/天, 1.5 亿点击/天, 100 万活跃广告 |
| 峰值 QPS | 展示 350K/sec, 点击 8.5K/sec |
| 端到端延迟 | <1 分钟（实时聚合路径） |
| 存储 | Parquet 压缩 750GB/天, 90 天归档 67TB; ClickHouse 聚合 144GB/天 |
| 架构模式 | **Lambda**（计费需精确, BF 0.01% 误报需批校准）vs Kappa |
| 聚合精度 | **精确 HashMap** 100 万广告 200MB（vs CMS 近似不能计费） |
| OLAP 引擎 | **ClickHouse**（向量化, 比 Druid 快 2-3x） |
| 去重 | **Bloom Filter + RocksDB** 两级（BF 1.5GB 1 小时窗口） |
| 欺诈检测 | 实时规则 <10ms + 批 ML 回溯（混合） |
| 投递语义 | Flink **exactly-once** + Kafka min.insync.replicas=2 |
| 多 DC | 边缘摄入 + MirrorMaker 2 集中聚合 |
| CAP 取向 | **计费 CP**（不可超付/漏付）/ **分析 AP**（dashboard 过时优于不可用） |
""",

    "interview-video-streaming": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 10 亿 DAU, 50 亿播放/天, 5000 万 PCU, 10 亿+ 视频 |
| 峰值 QPS | 播放 174K, 片段 10M（CDN 承载） |
| 出站带宽 | ~700 Gbps; CDN 95% 命中 → 源站 ~35 Gbps |
| 存储 | ~600 PB/年（优化后, 冷存储+长尾删 4K） |
| CDN | 200+ POP, **多 CDN**（CloudFront 主 + Akamai 备, DNS 切换） |
| 转码 | 3000+ GPU Workers, **混合**: 头部预转码 / 长尾 JIT |
| 编码 | H.264 + **AV1**（压缩好 30-50%, 编码慢 10x, 渐进迁移） |
| 分段协议 | **HLS** (iOS) + **DASH** (Android, LL-DASH ~3s 直播) |
| 协议层 | **ABR (Adaptive Bitrate)**, 6 分辨率（240p..4K） |
| 元数据 | MySQL + Redis + Elasticsearch（事务/缓存/搜索） |
| 多 DC | 3 主区 + GeoDNS, S3 CRR; 元数据单主 + 半同步 |
| CAP 取向 | 播放 **AP** / 上传元数据 **CP**（read-after-write） |
""",

    "interview-cloud-storage": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 5 亿注册, 1 亿 DAU, 1000 亿文件, 35 PB 去重后 |
| 峰值 QPS | 同步 17.4K, Chunk 52K, 元数据读 856K（50:1） |
| 带宽 | 上传峰 7.2 Gbps, 下载峰 18 Gbps |
| 长连接 | 5000 万 WebSocket（vs 轮询 1.67M QPS） |
| 分块策略 | **CDC (Content-Defined Chunking)** Rabin 指纹（vs 4MB 固定） |
| 去重粒度 | **Chunk 级**（vs 文件级, 部分相同也省传输） |
| 冲突解决 | **创建冲突副本**（vs LWW 静默丢失, 冲突<0.01%） |
| 通知机制 | **WebSocket** + 断线 exp-backoff（1/2/4/8s, max 30s） |
| 元数据存储 | **MySQL + Vitess 分片**（树形结构 + 跨子事务） |
| 多 DC | **Active-Passive** Dropbox 模式（主 + 灾备） |
| 复制 | MySQL **半同步** RPO=0; S3 **CRR** 异步 <15min |
| CAP 取向 | 元数据 **CP**（设备一致）/ 内容 chunk **AP** |
""",

    "interview-online-judge": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 注册 500 万, DAU 50 万, 日提交 100 万, 题库 3000 道 |
| 峰值 QPS | 平均 12, 竞赛峰值 120（10x）, 单场竞赛 5000 人 ~42 QPS |
| 判题时长 | 平均 10s（编译 2s + 50 用例 x 160ms） |
| 并发 Worker | 峰值 1200 容器槽位（每机 4 槽, 30 基础 → 弹性 300 台） |
| 沙箱 | **gVisor (runsc)** 系统调用拦截（vs Docker+seccomp 易遗漏） |
| 消息队列 | **RabbitMQ** 优先级队列 + ACK/NACK（vs Kafka 日志语义过度设计） |
| 判题粒度 | **逐测试用例** + 首个 WA early-termination |
| 排行榜 | **Redis Sorted Set** + 异步 Consumer 2-3s 延迟 |
| 测试用例 | **S3** (1KB-100MB, 总 ~40GB)（vs DB BLOB 影响备份） |
| 提交存储 | PostgreSQL 按月分区, ~1 TB/年 |
| 弹性伸缩 | 竞赛前 10 分钟预热 (Pre-warm) + Auto Scaling |
| CAP 取向 | 判题 **CP**（结果必准）/ 排行榜 **AP** / 题目 **AP** (CDN) |
""",

    "interview-ticket-reservation": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 注册 5000 万, DAU 200 万, 日订单 50 万 |
| 峰值 QPS | 搜索 580, 选座 15K（虚拟队列控制后） |
| Flash Sale | 100 万并发, 第一秒 50 万请求 → 虚拟队列削峰 |
| 虚拟队列吞吐 | 3 万用户/分钟（5000 人/批 x 6 批/分钟） |
| 并发控制 | **悲观锁 SELECT FOR UPDATE SKIP LOCKED**（vs 乐观锁热门座位 >90% 冲突） |
| 预留状态 | **DB + Redis TTL** 双写, 10 分钟 TTL 自动释放 |
| 抢票方式 | **虚拟队列**（vs 直接抢必崩, 队列以等待换稳定+公平） |
| 超售策略 | 票务严禁超售; 酒店按历史 no-show 率超售 5-8% |
| 支付方式 | **同步支付**（库存珍贵, 必须支付成功才确认） |
| 座位缓存 | Redis 10GB（1000 活动 x 50K 座位 x 200B） |
| 多 DC | **Active-Passive**（强一致不超卖, 跨区 +60-80ms 写延迟） |
| CAP 取向 | **CP**（不超卖>可用性, 主 DC 故障 30s Patroni 切换） |
""",

    "interview-web-crawler": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 目标 | 月抓 150 亿页, 已知 URL 100 亿 |
| 抓取速率 | 5787 pages/sec 平均, 17K 峰值（3x） |
| URL 发现 | 290K URLs/sec, 新 URL 29K/sec（10% 通过去重） |
| 节点数 | 35-63 台并发爬虫 |
| 带宽 | 4.6 Gbps 平均, 峰 13.8 Gbps |
| 存储 | 300 TB/月 HTML 压缩 + 150 TB/月文本 ≈ 10 TB/天 |
| URL 去重 | **Bloom Filter** 11.2GB (FPR 1%) + RocksDB 二级（vs HashSet 2TB） |
| 分配策略 | **一致性哈希按域名**（去中心化 + 同域串行 politeness）vs 中央调度器 |
| 内容去重 | **SimHash** 64-bit, 汉明距离 ≤3 即重复（vs MD5 模板页面误判） |
| 礼貌性 | 遵守 robots.txt + per-domain rate limit + DNS 缓存 |
| Frontier | **RocksDB 持久化**（爬虫跑数周, 节点宕机不丢 URL）<1ms 写入 |
| 内容存储 | **原始 HTML + 提取文本都存**（重解析无需重爬, 多 10x 但省带宽） |
""",

    "interview-auction-system": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | DAU 1 亿, 5000 万活跃拍卖, 日新建 500 万 |
| 峰值 QPS | 出价 8.3K, 详情读 248K（50:1 读写比） |
| WebSocket | 1M 并发, 20 台服务器（每台 50K 连接） |
| 存储 | 出价 28.6GB/天 → 10.4TB/年; Redis 30GB |
| 并发控制 | **Redis 分布式锁 (SETNX)**（vs 乐观锁 >50% 重试） |
| 实时推送 | **WebSocket** 全双工 + 心跳（vs SSE 单向） |
| 出价存储 | **正常实时写 PG / 热门 Kafka 异步**（延迟阈值降级） |
| 结束检测 | **Redis ZSET 延迟队列**（RDB/AOF 持久）+ 轮询 |
| 防狙击 | 末 3 分钟内出价 → 自动延长 2 分钟 |
| 多 DC | **Active-Passive**（CP, 跨区 +60-80ms 写延迟） |
| 故障切换 | Patroni RPO=0 / RTO <30s; Scheduler etcd Leader |
| CAP 取向 | 出价 **CP**（绝不双中标）/ 浏览 **AP** |
""",

    "interview-distributed-cache": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | DAU 5000 万, 读 100 次/写 10 次每用户每天 |
| 峰值 QPS | 读 173.6K, 写 17.4K, 命中率目标 95%+ |
| 容量 | 有效缓存 200GB（300GB 含元数据 1.5x 冗余） |
| 集群规模 | 10 节点（5 Primary + 5 Replica）, 单节点 64GB |
| 延迟 SLA | 读 P99 <1ms（同 DC）, 写 P99 <5ms |
| 缓存模式 | **Cache-Aside**（应用层管理）vs Write-Through（写延迟翻倍） |
| 数据分布 | **一致性哈希 + 虚拟节点**, 节点增减迁移 1/N（vs Range 热点不均） |
| 路由方式 | **Client-side Smart Client**（少 0.5ms hop）vs Proxy |
| 复制方式 | **异步复制**（写不等 ACK, 故障可丢几秒） |
| 淘汰策略 | **LRU 默认 / TinyLFU 可选**（扫描型 LFU 更优） |
| 故障检测 | Gossip 心跳 3s 超时 + Sentinel 自动切换 <5s |
| 多 DC | **每 DC 独立缓存层**, DB 跨区复制兜底 |
| CAP 取向 | **AP**（缓存是加速层非真相源, 等 TTL 自愈） |
""",
}

TARGET_SLUGS = list(CHEAT_SHEETS.keys())


def main() -> None:
    """UPSERT cheat_sheet for the 9 interview system designs (batch 3)."""
    init_db()
    db = SessionLocal()
    chinese_pattern = re.compile(r"[一-鿿]")
    failed: list[str] = []
    try:
        for slug in TARGET_SLUGS:
            row = db.query(SystemDesign).filter(SystemDesign.slug == slug).first()
            if row is None:
                print(f"[ERROR] slug not found: {slug}")
                failed.append(slug)
                continue

            new = CHEAT_SHEETS[slug]
            old = row.cheat_sheet or ""
            action = "NOOP" if old == new else ("INSERT" if not old else "UPDATE")
            row.cheat_sheet = new

            char_len = len(new)
            has_cn = bool(chinese_pattern.search(new))
            warn = ""
            if not has_cn:
                warn += " [WARN: no CN chars]"
            if char_len < 250 or char_len > 700:
                warn += f" [WARN: len {char_len} outside 250-700]"

            print(f"[{action}] {slug}: cheat_sheet={char_len} chars{warn}")

        db.commit()
        if failed:
            print(f"[FAIL] {len(failed)} slug(s) not found: {failed}")
            sys.exit(1)
        print(f"[DONE] cheat_sheet patched for {len(TARGET_SLUGS)} interview SDs (batch 3).")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
