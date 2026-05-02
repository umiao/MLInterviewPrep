"""Backfill cheat_sheet column for interview SDs id=9..18 (batch 2 of T-P2-683).

Targets (display_order 100-109, all currently empty on cheat_sheet):
  id=9  interview-url-shortener
  id=10 interview-rate-limiter
  id=11 interview-notification-system
  id=12 interview-ride-sharing
  id=13 interview-proximity-service
  id=14 interview-game-leaderboard
  id=15 interview-news-feed
  id=16 interview-chat-system
  id=17 interview-live-comments
  id=18 interview-search-autocomplete

Idempotent: rewrites only the cheat_sheet column for the 10 target slugs;
all other columns are left untouched.

Style (per project memory feedback_content_style_cn_en + 2026-05-02 batch 1
reference seed_sd_cheat_sheets_ebay_20260502.py):
  - Markdown table with 8-12 rows.
  - Columns: 'Item' / 'Number / Decision'.
  - Chinese narration + English technical-term expansion on first use.
  - 250-700 chars (compact flash card).
  - Numbers / decisions sourced from each row's existing overview /
    production_constraints / tradeoffs / formulas columns -- no new content
    invented.

Part of T-P2-683 (batch 2 of ~3-4); subsequent batches handle remaining
9 interview SDs (id=19..28 except 23) and 5 old Pinterest SDs (id=29..31, 33, 34).
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
    "interview-url-shortener": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 1 亿 DAU, 读写比 100:1, 5 年 18 亿 URL |
| 峰值 QPS | 读 35K, 写 350 |
| 存储 | ~30TB（含副本）, 单条 ~500 bytes |
| 短码空间 | 7 字符 **Base62** = $62^7 \\approx 3.5 \\times 10^{12}$ |
| ID 生成 | **Snowflake** + Base62（零碰撞 vs Hash 截断） |
| 重定向码 | **302 Found**（保留分析）vs 301（CDN 缓存） |
| 缓存策略 | **Cache-Aside** + Redis 2-5GB（80-20 法则） |
| 延迟 SLA | 重定向 P99<10ms, 缩短 P99<100ms |
| 数据库 | SQL 起步, DynamoDB 备选（KV 模式天然适配） |
| 分析管道 | 异步 Kafka（解耦核心读路径） |
| 多 DC | Active-Active + GeoDNS, 异步复制 <200ms |
| CAP 取向 | **AP 偏好**（读路径优先可用性） |
""",

    "interview-rate-limiter": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 5000 万 DAU, 峰值 350K QPS（API 入口层） |
| 限流检查延迟 | P99 <1ms（关键路径必须极快） |
| 活跃 key 数 | ~2.5 亿, Redis 集群 20-30GB / 4-8 分片 |
| 算法选择 | **Sliding Window Counter**（误差<1%, 无窗口边界）vs Token Bucket |
| 计数器存储 | **Redis** + Lua 脚本（原子检查+更新, 解决 TOCTOU 竞态） |
| 故障模式 | **Fail-open**（限流故障放行, 后端自身有过载保护兜底） |
| 规则存储 | **etcd**（watch 热更新 <1s 生效）vs YAML 文件 |
| 限流粒度 | 每 DC 独立（性能优先）+ 安全场景全局（精确优先） |
| 跨 DC 同步 | 异步 5-10s 汇总（"大致全局精确"） |
| 响应头 | `X-RateLimit-Limit/Remaining/Retry-After` + HTTP 429 |
| 允许误差 | 多实例并发可超限 1-3%（AP 优先, 大多数场景可接受） |
""",

    "interview-notification-system": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 1 亿 DAU, 日发 5 亿条, 峰值 30K QPS（大促 60K） |
| 渠道分布 | Push 60% / Email 25% / SMS 10% / In-App 5% |
| 单条成本 | Push ~免费, Email $0.0001, SMS $0.01-0.05 |
| 送达率 | Push 70-90%, SMS 95-99%, Email 80-95% |
| 队列 | **Kafka** 3 topic 按优先级（P0/P1/P2）, RF=3 |
| 投递语义 | **At-least-once** + 幂等 key（OTP 不可丢, 允许极少重复） |
| 模板渲染 | Worker 端（解耦 API, 按需加载缓存） |
| 多渠道策略 | P0 并行所有渠道, P1/P2 Push 优先失败降级 SMS |
| 提供商冗余 | Twilio<->Vonage, SES<->SendGrid（failover） |
| 用户偏好 | Cache-Aside + 写时失效（DB 写后主动删 Redis） |
| 紧急延迟 | OTP <5s, 普通 <30s, 营销分钟级 |
| 持久化 | 全量 90 天（投诉排查/审计）, 之后归档 S3 |
""",

    "interview-ride-sharing": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 2000 万乘客 DAU, 100 万司机, 1500 万订单/天 |
| 位置更新 QPS | ~333K（100 万司机 x 每 3s 一次） |
| WS 并发 | ~150 万长连接（Go Gateway 10 万/实例 x 15） |
| 位置存储 | **Redis Geospatial**（GEOADD/GEOSEARCH, $O(\\log N)$ <1ms） |
| 实时通信 | **WebSocket** 双向（vs Long Polling 高开销） |
| 匹配算法 | 低峰 Greedy 5ms, 高峰 **Batch Matching** 2s 一批全局最优 |
| ETA 分层 | 粗筛 Haversine → top-K Routing → 自有 ML |
| 互斥匹配 | Redis `SETNX lock:driver:{id}` + DB 行锁（强一致） |
| 动态定价 | 按 1km Geohash cell 分区（避免全城涨价） |
| Trip DB | **PostgreSQL**（多表关联 + ACID）vs DynamoDB |
| 批量写 Redis | Gateway 攒批 100ms / 100-500 条 pipeline |
""",

    "interview-proximity-service": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 5000 万 DAU, 2 亿商家, 2.5 亿次搜索/天 |
| 峰值 QPS | 搜索 5.8K, 详情 11.6K, 更新 <100（读写比 99:1） |
| 空间索引 | **Geohash**（一维编码 + B-Tree, 持久化友好）vs QuadTree（内存树） |
| Geohash 长度 | 6 字符 = 1.2km x 0.6km（默认搜索半径） |
| 多级缓存 | L1 Caffeine 30s（命中 40-60%）+ L2 Redis 5min（命中 80-90%）→ L3 MySQL |
| 缓存效果 | L1+L2 命中 >95%, 实际打 DB <300 QPS |
| 搜索引擎 | 自建 Geohash + MySQL（运维简单）vs Elasticsearch（杀鸡用牛刀） |
| 索引更新 | Kafka 异步增量 + 凌晨全量重建（兜底一致性） |
| 排序公式 | 综合评分（距离 + 评分 + 热度加权）vs 纯距离 |
| 评价去重 | DB 唯一约束 `(user_id, business_id)` + 应用层校验 |
| 一致性 | 整体 AP（新店 1-5 分钟可搜到, 评分 30s 生效） |
| 商家更新 | 写后 invalidate 缓存（read-after-write 一致） |
""",

    "interview-game-leaderboard": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 5000 万玩家, 500 万 DAU, 50 万 PCU |
| 峰值 QPS | 积分 5.8K（赛季 50K）, 查询 2.9K |
| 排行榜引擎 | **Redis Sorted Set** ZREVRANK $O(\\log N)$, ~5.7GB |
| 写入路径 | 同步 vs **Kafka 异步**（削峰 + 重放, +200ms） |
| 持久化 | Redis + MySQL 双写（兜底重建） |
| 多维度 | 日/周/赛季 **独立 Sorted Set** 各一次 ZADD |
| 同分排序 | 时间戳编码进 score 低位（先到先得） |
| 分片策略 | >1 亿玩家按 **score range** 分 Shard |
| 全局排名 | rank_in_shard + $\\sum$ ZCARD(更高 shard) |
| 多 DC | 全局主 + 区域只读副本（100-500ms） |
| CAP 取向 | **AP**（赛季结算: 停写 2-3s 取一致快照） |
| 成本 | ~$1,600/月（Redis+Kafka+MySQL） |
""",

    "interview-news-feed": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 5 亿注册, 2 亿 DAU, 平均关注 200, 日发 2000 万 |
| 峰值 QPS | Feed 读 115K, 发帖 700, Fan-out 写 140K |
| Feed 缓存 | 3.6TB Redis（30 天活跃 3 亿用户, 命中 95%+） |
| Fan-out 策略 | **Hybrid**: 普通用户 Push, 名人（>1000 万粉）Pull |
| 缓存结构 | **Redis Sorted Set**（按 score 插入+去重） |
| 排序 | **ML 模型**（停留 +30-50%）, 时间序降级 |
| 帖子 ID | **Snowflake** 64-bit（时间有序, 省 50% vs UUID） |
| Read-your-own-writes | 发帖后写自己 Feed 缓存保证立即可见 |
| 排序双阶段 | CPU 粗排 1000→200, GPU 精排 200→top |
| 媒体 | 3 分辨率（缩略/标准/原图）+ 热门 CDN 预热 |
| 多 DC | Active-Active GeoDNS + MirrorMaker 2 跨 DC |
| 降级 | Ranking 故障→时间序; Feed 缓存失效→ DB 重建 |
""",

    "interview-chat-system": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 10 亿注册, 5 亿 DAU, 1 亿 PCU = 1 亿 WS 连接 |
| 峰值 QPS | 发送 690K, 投递 3.5M, 日新消息 1000 亿 |
| 延迟 | 同 DC P99 <300ms, 跨 DC <1s |
| 传输协议 | **WebSocket** 双向 50ms（vs Long Polling 1s） |
| Gateway 容量 | 50K 连接/实例（epoll/Netty, 10-20KB/连接） |
| 消息存储 | **Cassandra** RF=3 QUORUM（3.5M/s 写） |
| 群上限 | 500 人 → **写时扇出**（vs 读时合并） |
| 送达保证 | **At-least-once + Dedup**（client_message_id） |
| 在线状态 | 延迟聚合（30s 轮询 + 按需查, 省 90% 流量） |
| 消息 ID | **Snowflake** 单节点单调（时钟+序列号） |
| 多 DC | NetworkTopologyStrategy 内置多 DC |
| 冷热分离 | 7 天 SSD + 冷数据 HDD 压缩 |
""",

    "interview-live-comments": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 1 万场同时直播, 1 亿并发观众, 热门场 1000 万观众 |
| 评论写入 QPS | 全平台峰值 500K, 热门场 100K 条/秒 |
| Edge Node | 5000 个, 出站带宽 ~200 GB/s |
| 传输协议 | **SSE (Server-Sent Events)** 单向（HTTP 兼容 + Last-Event-ID 自动重连） |
| 一致性 | **采样**（>50/s 启动, 每观众 ~30/s 子集, 客户端可读） |
| 送达保证 | **At-most-once**（vs Chat 的 at-least-once, 漏一条可容忍） |
| 审核 | **Pre-moderation** 两级: 关键词 <1ms + ML 异步 ~10ms |
| 评论存储 | 异步批量写 Cassandra 90 天（不阻塞实时分发） |
| 速率限制 | 用户 5 条/分钟, 直播间 >100K/s 自动 slow mode 30s/条 |
| 扇出树 | Dispatcher → Regional Relay → Edge Node（多级聚合 + 500ms 批） |
| 表情反应 | 近似计数 **HyperLogLog** 或 Redis INCR 聚合 |
| 多 DC | GeoDNS + 跨 DC 专线（同区 <50ms, 跨区 <200ms） |
""",

    "interview-search-autocomplete": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 10 亿 DAU, 5000 万不同查询, Trie 总 84GB / 12 节点 |
| 峰值 QPS | 原始 ~800K, 到 Trie ~336K（CDN 40% + App Cache 30% 卸载） |
| 延迟 SLA | P99 <100ms（>200ms 用户放弃自动补全直接回车） |
| 数据结构 | **Trie 前缀树** $O(p)$ 查找（vs Inverted Index 不擅前缀） |
| Trie 更新 | **批量重建** 15 分钟 + 趋势注入秒级（实时 CAS 不现实） |
| 多语言 | **分语言 Trie**（中文拼音 vs 英文空格分词不可统一） |
| 缓存层级 | 浏览器 + CDN 5min + App Cache 15min（TTL 最终一致） |
| 个性化 | **混合**: 服务端全局 top-K + 客户端本地历史二次混排（保 CDN 命中） |
| 不雅过滤 | 构建时过滤（运行时零开销）vs 查询时过滤 |
| 前端 debounce | 50-100ms 等输入停顿（实际 QPS 降 50-70%） |
| 请求合并 | App Cache **singleflight**（相同前缀只 1 次穿透 Trie） |
| 多 DC | 各区域全 Trie 副本（7GB 足够小, GeoDNS 路由不跨区） |
""",
}

TARGET_SLUGS = list(CHEAT_SHEETS.keys())


def main() -> None:
    """UPSERT cheat_sheet for the 10 interview system designs (batch 2)."""
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
        print(f"[DONE] cheat_sheet patched for {len(TARGET_SLUGS)} interview SDs (batch 2).")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
