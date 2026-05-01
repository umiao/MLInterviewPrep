"""Seed Meta System Design 备战汇总 (24 SD topics consolidation page).

Per T-P0-269 (META-SD-6). Target: company_documents row for company_id=31
(Meta) titled '[Meta] System Design 备战汇总 (24 SD topics)'.

Goal: a one-page list the user can scan on the Meta drawer interview morning.
Each of the 24 SD modules (20 existing + 4 [NEW] from T-P0-265..268) gets:
  - the slug as a code span
  - a ~30-char Meta-视角 punchline (what Meta cares about for that topic)
  - one likely 高频追问 (interviewer follow-up)

DELIBERATELY plain markdown -- NO `db://` deep links. Per memory
`feedback_dblc_drawer_links.md`: a `db://N` whose N happens to be a
company_documents PK silently opens the wrong drawer (numerically-
coincident LC problem); this hub references SD slugs (which live in the
`system_designs` table, not `problems` / `company_documents`), so a
db:// link here would route to the wrong surface entirely. Slug-only
keeps the routing layer honest.

Idempotency: sentinel <!-- META_SD_SUMMARY_20260430 --> gates the write.
Second run = 0 writes when content is byte-identical.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- META_SD_SUMMARY_20260430 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta] System Design 备战汇总 (24 SD topics)"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"

# Order: 20 existing first (mirrors task spec coverage list), then 4 [NEW].
# Each tuple = (slug, is_new, punchline, followup).
ENTRIES: tuple[tuple[str, bool, str, str], ...] = (
    (
        "interview-news-feed",
        False,
        "IG 写扩散 vs 读聚合 hybrid; 头部账户走 pull",
        "明星 1 亿 follower 怎么 fan-out 不爆扇出？",
    ),
    (
        "interview-chat-system",
        False,
        "WhatsApp E2EE Signal 协议 + last-seen 最终一致",
        "群聊 256 人怎么做 forward secrecy 密钥棘轮？",
    ),
    (
        "interview-live-comments",
        False,
        "IG Live pub-sub 全序 + 高扇出限速降级",
        "百万观众 spike 怎么保证不丢评论顺序？",
    ),
    (
        "interview-search-autocomplete",
        False,
        "IG 搜索 trie + n-gram, freshness 加权 BM25",
        "突发热点几秒内进 suggestion 怎么做？",
    ),
    (
        "interview-top-k-heavy-hitters",
        False,
        "Count-Min Sketch + Misra-Gries 流式近似",
        "为什么 99% 准确够用，不上精确计数？",
    ),
    (
        "interview-ad-click-aggregator",
        False,
        "Meta Ads Lambda 架构 + 幂等 ID exactly-once",
        "广告主重试导致重复扣费怎么避免？",
    ),
    (
        "interview-video-streaming",
        False,
        "FB Watch HLS/DASH 码率梯 + 预测预热 CDN",
        "突发病毒视频 CDN 边缘节点怎么扩容？",
    ),
    (
        "interview-cloud-storage",
        False,
        "Workplace 滚动哈希 chunk dedup + 增量同步",
        "10GB 大文件断点续传 + 弱网怎么设计？",
    ),
    (
        "interview-price-drop-tracker",
        False,
        "Marketplace 时序存储 + 多渠道告警 fanout",
        "用户屏蔽商品后已发告警怎么撤回？",
    ),
    (
        "interview-online-judge",
        False,
        "Bootcamp gVisor / Firecracker 沙箱 + 队列",
        "怎么防止用户提交挖矿 / fork 炸弹？",
    ),
    (
        "interview-ticket-reservation",
        False,
        "FB Events hold-tier + 分布式锁 vs 乐观锁",
        "高并发抢票悲观还是乐观锁？怎么选？",
    ),
    (
        "interview-web-crawler",
        False,
        "⭐ Leaderless 10K + Paxos exactly-once + 100MB/机 set",
        "URL 去重为什么不用 Bloom Filter？",
    ),
    (
        "interview-auction-system",
        False,
        "Marketplace 实时撮合 + 反 snipe 延时延期",
        "出价相同 tie-break 用时间序还是 ID 序？",
    ),
    (
        "interview-proximity-service",
        False,
        "Nearby Friends geohash / H3 + 圈内 ANN",
        "用户位置精度怎么模糊化防泄漏？",
    ),
    (
        "interview-distributed-cache",
        False,
        "TAO 一致性哈希 + LRU/LFU + write-through",
        "热点 key 击穿 / 穿透 / 雪崩怎么救？",
    ),
    (
        "interview-rate-limiter",
        False,
        "API Gateway 令牌桶 + Redis Lua 原子化",
        "Lua 脚本单线程瓶颈怎么水平扩展？",
    ),
    (
        "interview-notification-system",
        False,
        "Push 优先队列 + 多 channel (APNS/FCM/SMS)",
        "iOS APNS 失败怎么 fallback 多通道？",
    ),
    (
        "interview-ride-sharing",
        False,
        "司机匹配 + ETA 预测 + surge pricing",
        "司机端断网时 dispatch 怎么 reassign？",
    ),
    (
        "interview-game-leaderboard",
        False,
        "IG Reels Redis ZSet 分片 + 周期合并",
        "千万级玩家怎么算 top-K 和 percentile？",
    ),
    (
        "interview-url-shortener",
        False,
        "Internal base62 + 计数器分片 + 热链缓存",
        "短链冲突 + 自定义 vanity 怎么共存？",
    ),
    # --- 4 [NEW] entries from T-P0-265..268 ---
    (
        "interview-harmful-content-detection",
        True,
        "多阶段 pipeline edge filter → ML → 人审",
        "对抗扰动让模型失效，怎么持续学习？",
    ),
    (
        "interview-fb-post-privacy",
        True,
        "5-tier visibility + audience 求交 + 隐私衰减",
        "Friends-of-Friends 怎么实时算交集？",
    ),
    (
        "interview-spotify-audio-streaming",
        True,
        "Codec ladder + offline DRM + Discover Weekly CF",
        "Discover Weekly 新用户 cold start 怎么破？",
    ),
    (
        "interview-recommendation-system",
        True,
        "Two-tower → DLRM / MMoE → MMR diversity 重排",
        "MMoE expert 数 4 还是 8？怎么定？",
    ),
)


def _build_content() -> str:
    """Assemble the markdown payload from ENTRIES."""
    lines: list[str] = [
        SENTINEL,
        "",
        "# Meta — System Design 备战汇总 (24 SD topics)",
        "",
        "> **用法**: 面试当天早上扫这一页。每条给一句 Meta-视角 punchline + 一个高频追问，确认自己每个题都能口述 30-60 秒大纲；卡壳的题打开对应 SD 卡片复习。",
        "> **覆盖**: 20 个既有 SD（按 Meta 历年高频排序）+ 4 个 [NEW] (本周新增，覆盖 Privacy / Audio / Reco / Trust&Safety 四个 Meta 强信号方向)。",
        "",
        f"**总条目**: {len(ENTRIES)}（{sum(1 for e in ENTRIES if not e[1])} 既有 + {sum(1 for e in ENTRIES if e[1])} [NEW]）",
        "",
        "---",
        "",
        "## 既有 SD 题库",
        "",
    ]
    for slug, is_new, punchline, followup in ENTRIES:
        if is_new:
            continue
        lines.append(
            f"- `{slug}` — {punchline}; 高频追问: \"{followup}\""
        )
    lines.extend([
        "",
        "---",
        "",
        "## [NEW] 本周新增 (T-P0-265..268)",
        "",
    ])
    for slug, is_new, punchline, followup in ENTRIES:
        if not is_new:
            continue
        lines.append(
            f"- **[NEW]** `{slug}` — {punchline}; 高频追问: \"{followup}\""
        )
    lines.extend([
        "",
        "---",
        "",
        "## 离场 checklist (面试前 60 秒扫)",
        "",
        "1. 每个 slug 都能在 60 秒内说出 architecture 主图（4-5 个 box）？",
        "2. 每个 punchline 关键词（如 \"Lambda 架构\" / \"E2EE\" / \"令牌桶\"）能展开 1 个 tradeoff？",
        "3. 高频追问遇到陌生项立刻找对应 SD 卡片复习（不要硬编）。",
        "4. 不在本表的题目（如 design Twitter）就当作 news-feed + chat-system 的组合即兴拼装。",
        "",
    ])
    return "\n".join(lines) + "\n"


CONTENT = _build_content()


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_content(content: str) -> None:
    """Cheap structural checks on the content payload."""
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing")
    required_markers = (
        "# Meta — System Design 备战汇总",
        "## 既有 SD 题库",
        "## [NEW] 本周新增",
        "## 离场 checklist",
    )
    for marker in required_markers:
        if marker not in content:
            raise RuntimeError(f"section marker missing: {marker!r}")

    # All 24 slugs must appear exactly once as `interview-X` code-span.
    for slug, _, _, _ in ENTRIES:
        token = f"`{slug}`"
        n = content.count(token)
        if n != 1:
            raise RuntimeError(
                f"expected exactly 1 occurrence of {token}, got {n}"
            )

    # 20 既有 + 4 [NEW] partition must hold.
    n_new = sum(1 for e in ENTRIES if e[1])
    n_existing = len(ENTRIES) - n_new
    if (n_existing, n_new) != (20, 4):
        raise RuntimeError(
            f"partition wrong: existing={n_existing} new={n_new} (want 20+4)"
        )

    # Memory feedback_dblc_drawer_links.md: NO db:// or cd:// or lc:// links.
    for scheme in ("db://", "cd://", "lc://"):
        if scheme in content:
            raise RuntimeError(
                f"forbidden URI scheme {scheme!r} present -- "
                "this hub MUST be slug-only (avoid drawer corruption)"
            )

    # 高频追问 must appear at least once per entry.
    if content.count("高频追问:") != len(ENTRIES):
        raise RuntimeError(
            f"expected {len(ENTRIES)} '高频追问:' markers, "
            f"got {content.count('高频追问:')}"
        )


def main() -> int:
    """Upsert the Meta SD 备战汇总 doc (idempotent)."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    validate_content(CONTENT)
    print(f"[OK] content validated: len={len(CONTENT)} entries={len(ENTRIES)}")

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT name FROM companies WHERE id = ?", (COMPANY_ID,)
        ).fetchone()
        if row is None:
            print(f"[ERROR] company_id={COMPANY_ID} not found")
            return 1
        print(f"[OK] target company: id={COMPANY_ID} name={row[0]!r}")

        cur = conn.execute(
            "SELECT id, content FROM company_documents "
            "WHERE company_id = ? AND title = ?",
            (COMPANY_ID, DOC_TITLE),
        )
        existing = cur.fetchone()

        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        new_hash = sha256_bytes(CONTENT)

        if existing is None:
            conn.execute(
                "INSERT INTO company_documents "
                "(company_id, title, content, source_type, doc_kind, "
                "content_hash, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    COMPANY_ID,
                    DOC_TITLE,
                    CONTENT,
                    SOURCE_TYPE,
                    DOC_KIND,
                    new_hash,
                    now,
                    now,
                ),
            )
            conn.commit()
            new_id = conn.execute(
                "SELECT id FROM company_documents "
                "WHERE company_id = ? AND title = ?",
                (COMPANY_ID, DOC_TITLE),
            ).fetchone()[0]
            print(
                f"[INSERT] id={new_id} len={len(CONTENT)} "
                f"hash={new_hash[:12]}..."
            )
        else:
            existing_id, existing_content = existing
            if SENTINEL in existing_content and existing_content == CONTENT:
                print(
                    f"[UNCHANGED] id={existing_id} sentinel present + "
                    f"content byte-identical; 0 writes"
                )
            else:
                conn.execute(
                    "UPDATE company_documents "
                    "SET content = ?, content_hash = ?, updated_at = ? "
                    "WHERE id = ?",
                    (CONTENT, new_hash, now, existing_id),
                )
                conn.commit()
                old_len = len(existing_content)
                print(
                    f"[UPDATE] id={existing_id} old_len={old_len} "
                    f"new_len={len(CONTENT)} delta={len(CONTENT) - old_len:+d}"
                )

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
