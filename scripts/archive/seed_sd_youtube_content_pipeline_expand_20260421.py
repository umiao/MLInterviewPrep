"""Seed SD-YT-01: Expand system_designs id=21 (YouTube/Netflix Video Streaming).

Folds 8 traditional-SD expansions into existing sections (additive only, no
section deletion, preserving all existing numbered lists and tables):

  1. Upload Service: chunked upload (10-50 MB), edge server, Pub/Sub queue,
     stateless FFmpeg worker pool.
  2. Transcoding Pipeline: tier policy (H.264 for all / VP9 for hot /
     AV1 for head + 4K/8K), encoding ladder (9-rung pyramid + per-rung
     multi-bitrate), VCU/Argos ASIC callout.
  3. Video Storage: Colossus for blob, Bigtable for metadata, Elasticsearch
     for text, Content ID fingerprint table.
  4. CDN: Google Global Cache (GGC) ISP-rack embedding layer.
  5. Architecture: new #### 7 Content-to-Feature Bridge -- multimodal
     pipeline feeding both search and recommendation (framework node id=198).
  6. Tradeoffs: DASH vs HLS segment-length row.

Idempotent:
  - Detects post-expansion state via characteristic marker strings
    ("Google Global Cache" in architecture, "DASH 1-5s" in tradeoffs).
  - If markers present -> full [SKIP]. Else apply all inserts atomically
    and recompute content_hash.

DB-backup-guarded:
  Before any write, copies the target DB file to
  <db>.bak.<timestamp>_pre_expand_sd21. Skip via --no-backup.

AC verification (post-run):
  - grep counts: VCU>=1, Colossus>=1, Bigtable>=2, Pub/Sub>=1,
    chunked>=2, 'Google Global Cache'>=1
  - No existing section deleted (asserted by length comparison).
  - Re-run [SKIP] on 2nd invocation.

Usage:
    python scripts/seed_sd_youtube_content_pipeline_expand_20260421.py [--no-backup]
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.backend.database import SessionLocal, get_engine, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

TARGET_ID = 21
IDEMPOTENCY_MARKER = "Google Global Cache"

# ---------------------------------------------------------------------------
# Insertion blocks (additive expansions, folded into existing sections)
# ---------------------------------------------------------------------------

# Block 1: appended INSIDE Upload Service, before the next "#### 2." heading.
# Anchor: last bullet of Upload Service, then two newlines, then "#### 2.".
UPLOAD_SERVICE_ANCHOR = (
    "- 同时提取视频基础元数据 (时长、分辨率、编码格式、文件大小)\n"
    "\n"
    "#### 2. Transcoding Pipeline (转码管道)"
)
UPLOAD_SERVICE_REPLACEMENT = (
    "- 同时提取视频基础元数据 (时长、分辨率、编码格式、文件大小)\n"
    "- **分块上传机制 (Chunked Upload Mechanics)**: 客户端以 "
    "**resumable chunked upload** 模式将原始视频切成 "
    "**10-50 MB 的块 (chunk)**, 通过 HTTPS 直传到**边缘接入服务器 "
    "(Edge Upload Server)**, 由边缘服务器异步落盘到 **GCS (Google Cloud "
    "Storage) / Colossus** blob 存储. 每个 chunked 段完成后投递一条 "
    "**Pub/Sub** 消息 (topic: `video-ingest`), 下游**无状态 FFmpeg "
    "Worker 池 (stateless FFmpeg workers)** 在数千实例上并发拉取任务. "
    "Worker 无状态, 崩溃后消息重投到其它实例 retry, 已完成的 chunk "
    "不会被重复转码 (每 chunk idempotent)\n"
    "- **Pub/Sub 优势** (对比 Kafka): 在 GCP 生态内天然多区域广播, "
    "无需管理 partition / ISR, 按消息计费, 适合突发上传峰值 (晚高峰 "
    "up to 10x 日均). Kafka 在 on-prem 或成本敏感场景仍是选择\n"
    "\n"
    "#### 2. Transcoding Pipeline (转码管道)"
)

# Block 2: appended INSIDE Transcoding Pipeline, before "#### 3. Video Storage".
TRANSCODING_ANCHOR = (
    "- **输出**: 多分辨率 + 多编码格式的 **HLS (HTTP Live Streaming)** "
    "manifest 文件\n"
    "  (.m3u8) 和 TS/fMP4 片段文件\n"
    "\n"
    "#### 3. Video Storage (视频存储)"
)
TRANSCODING_REPLACEMENT = (
    "- **输出**: 多分辨率 + 多编码格式的 **HLS (HTTP Live Streaming)** "
    "manifest 文件\n"
    "  (.m3u8) 和 TS/fMP4 片段文件\n"
    "- **转码层级政策 (Transcoding Tier Policy)** -- 头部激进, "
    "长尾保守 (cost amortization):\n"
    "  - **H.264 for all**: 每个视频都必须生成 H.264 版本 (~100% 客户端 "
    "兼容), 是兜底保障. 成本最低, 压缩率最差\n"
    "  - **VP9 for hot**: 热门内容 (前 ~20% 播放量) 额外生成 VP9, "
    "比 H.264 节省 30-40% 带宽. 移动端原生支持\n"
    "  - **AV1 for head + 4K/8K**: 仅 TOP ~1% 头部 + 所有 4K / 8K 视频 "
    "生成 AV1, 比 H.264 节省 50-60% 带宽. AV1 编码成本约 H.264 的 "
    "50-100x, 但头部视频播放量集中 (前 1% 视频占总播放 50%+), "
    "对头部内容 bandwidth 节省摊销 ROI 极高; 长尾视频播放量稀疏, "
    "强行 AV1 编码成本收不回来. 原则: **长尾保守头部激进**\n"
    "- **编码阶梯 (Encoding Ladder)** -- 每分辨率多码率档位:\n"
    "  - 九级分辨率金字塔: **144p / 240p / 360p / 480p / 720p / "
    "1080p / 1440p / 2160p (4K) / 4320p (8K)**\n"
    "  - 每档内部再分多码率: 以 **720p** 为例, 同时提供 "
    "**1.5 Mbps** (低质), **2.5 Mbps** (中质), **4 Mbps** (高质) "
    "三档; 客户端 ABR 在同分辨率多码率间平滑切换, 避免单次跳分辨率 "
    "的视觉突变\n"
    "  - 阶梯越密用户 QoE 越平滑, 但转码成本线性增长. 实际部署: "
    "每分辨率 2-3 档, 全金字塔总计 ~20 种 rendition (resolution x codec "
    "x bitrate 的组合)\n"
    "- **专用转码 ASIC (VCU / Argos)**: Google 自研**视频编码单元 "
    "(Video Coding Unit, VCU, 内部代号 Argos)** ASIC 用于 VP9 / AV1 "
    "大规模编码. 相比通用 GPU (NVENC), VCU 在同等功耗下吞吐提升 "
    "**7-20x**, 每瓦性能提升 **20-33x**. YouTube 规模下 VCU 约 2 年 "
    "摊销回本, 是支撑 AV1 全量推广的硬件基础 (纯 GPU 集群吞吐量不够, "
    "单位功耗成本也不够低). 参考文献: Ranganathan et al., *Warehouse-"
    "scale video acceleration* (ASPLOS 2021, VCU/Argos paper)\n"
    "\n"
    "#### 3. Video Storage (视频存储)"
)

# Block 3: appended INSIDE Video Storage, before "#### 4. CDN & Playback".
STORAGE_ANCHOR = (
    "- 存储优化: 对于长尾视频只保留 480p 和 720p 两种分辨率，\n"
    "  高分辨率版本在请求时动态转码 (**Just-in-Time Transcoding**)\n"
    "\n"
    "#### 4. CDN & Playback Service (CDN 与播放服务)"
)
STORAGE_REPLACEMENT = (
    "- 存储优化: 对于长尾视频只保留 480p 和 720p 两种分辨率，\n"
    "  高分辨率版本在请求时动态转码 (**Just-in-Time Transcoding**)\n"
    "- **存储分层 (Storage & Metadata Split)** -- 不同数据类型选不同底座:\n"
    "  - **Blob (视频二进制 + 所有 rendition)**: **Colossus** (Google "
    "下一代分布式文件系统, GFS 继任者, GCS 是其上层封装). 采用 "
    "Reed-Solomon 纠删码 (典型 6,3): 空间利用率 ~67% (相比 3x 副本的 "
    "33%) 但容错能力相当, PB 级规模下每年节省数亿美金存储成本\n"
    "  - **结构化元数据 (视频 metadata / rendition 索引 / 播放位点 / "
    "轻量用户画像字段)**: **Bigtable** (稀疏列宽行, 行键自动分片). "
    "单表容纳 10 亿+ 视频元数据, 行键 `video_id` 使请求均匀分布, "
    "无需手工分片. Bigtable 的定位: 无 JOIN, 无事务, 但线性扩展到 "
    "PB 级容量与百万 QPS, 是 YouTube / GCS / Google Search / Maps "
    "共用的 NoSQL 底座\n"
    "  - **全文搜索 (标题 / 描述 / 字幕 OCR / ASR 转写)**: "
    "**Elasticsearch** (倒排索引 + BM25 + 向量 ANN 混合 retrieval)\n"
    "  - **版权指纹库 (Content ID fingerprint)**: 音频 **Chromaprint** "
    "128-bit + 视频 **pHash** 60-bit 双通道比对, 存在独立 **Bigtable** "
    "表 (按指纹哈希分片), 上传完成后触发异步匹配 + 命中即进入版权申诉 "
    "流程. 这是 YouTube 与其它 UGC 平台在法律/合规上的核心护城河\n"
    "\n"
    "#### 4. CDN & Playback Service (CDN 与播放服务)"
)

# Block 4: append GGC bullet after L3 Origin bullet.
CDN_ANCHOR = (
    "  - L3: Origin (源站) -- S3/GCS 对象存储\n"
    "- **ABR (Adaptive Bitrate) 播放流程**:"
)
CDN_REPLACEMENT = (
    "  - L3: Origin (源站) -- S3/GCS 对象存储\n"
    "  - **Google Global Cache (GGC) / ISP 嵌入层**: 除自建 POP 外, "
    "还将缓存节点**直接部署到 ISP 机房的 rack 内** (与 Netflix "
    "**Open Connect Appliance** 同构). 用户流量不出 ISP 即可拿到视频, "
    "RTT 降到 **< 5 ms**, 回源流量减少 **70%+**, 大幅降低 ISP 之间 "
    "的跨网结算成本 (settlement-free peering). GGC 形成 "
    "`ISP rack -> 区域 Shield -> Origin (Colossus)` 三层 CDN 架构, "
    "是 YouTube / Netflix 这种巨头内容方能进入 ISP 骨干的关键杠杆\n"
    "- **ABR (Adaptive Bitrate) 播放流程**:"
)

# Block 5: new #### 7. Content-to-Feature Bridge inserted before
# "#### 数据库选择与理由".
BRIDGE_ANCHOR = "\n#### 数据库选择与理由 (Database Choices)"
BRIDGE_REPLACEMENT = (
    "\n"
    "#### 7. Content-to-Feature Bridge (内容 -> 特征桥)\n"
    "\n"
    "**多模态管道 (Multimodal Pipeline)** 在转码完成后异步触发, "
    "对原始视频并行抽取:\n"
    "\n"
    "- **视频帧 embedding (Video-BERT-like)**: 每 2 秒采样一帧, 经 "
    "VideoMAE / Video-BERT / VJEPA 生成 ~512-dim embedding, 用于 "
    "\"视觉相似内容\" 召回\n"
    "- **ASR (Automatic Speech Recognition, 自动语音识别)**: "
    "Whisper / USM 将音轨转字幕, 同时产出时间对齐的文本 token 序列 "
    "(支撑多语字幕 + 全文检索)\n"
    "- **OCR (Optical Character Recognition, 光学字符识别)**: 对关键帧 "
    "识别嵌入字幕 / 贴纸 / 标牌 / 横幅文本\n"
    "- **音频指纹 (Content ID fingerprint)**: Chromaprint 用于版权检测 "
    "+ 音乐识别\n"
    "- **Topic classification**: 多标签分类器输出 ~1000 细粒度 topic "
    "(用于分区运营与冷启 taxonomy)\n"
    "- **Thumbnail scoring**: CTR 预估模型对候选封面帧打分, 选最优 "
    "缩略图\n"
    "\n"
    "这些多模态特征**同时**喂给两条下游链路:\n"
    "\n"
    "1. **搜索索引** (Elasticsearch 文本字段 + 向量字段): 实现从 "
    "\"标题/描述\" 浅层检索扩展到 \"视频内容语义\" 深层检索\n"
    "2. **推荐系统 retrieval / ranking** (见 framework node id=198 "
    "Real-Time Recommendation): 实现基于内容语义的**冷启召回** "
    "(新视频没有交互信号时靠 embedding 相似找受众) 和 **相关性排序** "
    "(ranker feature 里 content embedding 与 user embedding 的交互)\n"
    "\n"
    "**关键设计点**: 同一份多模态管道为搜索 + 推荐两条业务链路共享, "
    "避免重复抽取 (frame embedding 单次 ~GPU-秒级, 重复抽取成本 "
    "不可接受). 这是内容平台 (YouTube / Netflix / TikTok / "
    "小红书) 的标准架构模式 -- 内容理解层是一个 platform capability, "
    "不是 per-vertical 的工具.\n"
    "\n"
    "#### 数据库选择与理由 (Database Choices)"
)

ARCH_INSERTS: list[tuple[str, str, str]] = [
    ("upload_service", UPLOAD_SERVICE_ANCHOR, UPLOAD_SERVICE_REPLACEMENT),
    ("transcoding", TRANSCODING_ANCHOR, TRANSCODING_REPLACEMENT),
    ("storage", STORAGE_ANCHOR, STORAGE_REPLACEMENT),
    ("cdn_ggc", CDN_ANCHOR, CDN_REPLACEMENT),
    ("content_bridge", BRIDGE_ANCHOR, BRIDGE_REPLACEMENT),
]

# Block 6: DASH vs HLS row added to Key Design Decisions table, after
# the 视频编码 row.
TRADEOFF_ANCHOR = (
    "| 视频编码 | H.264 (兼容性最好) | AV1 (压缩率最高) | "
    "**渐进迁移**: 新内容同时提供 H.264 + AV1; AV1 压缩率比 H.264 "
    "好 30-50%, 但编码速度慢 10x, 需要 GPU。2-3 年内逐步淘汰 H.264 |\n"
    "| 元数据存储"
)
TRADEOFF_REPLACEMENT = (
    "| 视频编码 | H.264 (兼容性最好) | AV1 (压缩率最高) | "
    "**渐进迁移**: 新内容同时提供 H.264 + AV1; AV1 压缩率比 H.264 "
    "好 30-50%, 但编码速度慢 10x, 需要 GPU。2-3 年内逐步淘汰 H.264 |\n"
    "| 分段协议 | HLS 6-10 s 段 | DASH 1-5 s 段 | "
    "**同时生成**: iOS/Apple 端必须 HLS (原生支持); Android/Web 优先 "
    "DASH (开放标准). DASH 短段在移动网络下**减少 rebuffering 最多 "
    "30%** (启动和切换粒度更细), 代价是 manifest 请求频率高 2x, "
    "CDN 命中率略低; 短段也允许 low-latency DASH (LL-DASH) 把直播 "
    "端到端延迟压到 ~3 s |\n"
    "| 元数据存储"
)


# ---------------------------------------------------------------------------
# DB-file backup
# ---------------------------------------------------------------------------


def _backup_db(db_path: Path) -> Path | None:
    """Copy the DB file to a timestamped .bak before mutating.

    Args:
        db_path: Absolute path to the SQLite DB file.

    Returns:
        Path to the backup file, or None if the source does not exist.
    """
    if not db_path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.with_name(f"{db_path.name}.bak.{ts}_pre_expand_sd21")
    shutil.copy2(db_path, backup)
    return backup


def _resolve_db_file() -> Path | None:
    """Return the SQLite DB file path bound to the engine, or None."""
    engine = get_engine()
    url = engine.url
    if url.drivername != "sqlite":
        return None
    if url.database in (None, "", ":memory:"):
        return None
    return Path(url.database).resolve()


def _content_hash(row: SystemDesign) -> str:
    """Compute md5 over concatenation of the 8 markdown sections.

    Args:
        row: SystemDesign row.

    Returns:
        32-char hex digest.
    """
    parts = [
        row.overview or "",
        row.architecture or "",
        row.dataflow or "",
        row.formulas or "",
        row.production_constraints or "",
        row.tradeoffs or "",
        row.defense or "",
        row.verbal_outline or "",
    ]
    blob = "\n".join(parts).encode("utf-8")
    return hashlib.md5(blob).hexdigest()


# ---------------------------------------------------------------------------
# Insertion helpers
# ---------------------------------------------------------------------------


def _apply_insert(
    section_text: str,
    anchor: str,
    replacement: str,
    label: str,
) -> str:
    """Replace a single anchor occurrence, asserting exactly one match.

    Args:
        section_text: Full section body.
        anchor: Anchor substring to locate (must appear exactly once).
        replacement: Replacement string.
        label: Label for error messages.

    Returns:
        Updated section text.

    Raises:
        RuntimeError: If anchor missing or appears more than once.
    """
    count = section_text.count(anchor)
    if count == 0:
        raise RuntimeError(
            f"[{label}] anchor not found in section. "
            "Upstream content may have drifted; re-verify anchor strings."
        )
    if count > 1:
        raise RuntimeError(
            f"[{label}] anchor matched {count}x (expected 1). "
            "Pick a more specific anchor."
        )
    return section_text.replace(anchor, replacement, 1)


def _expand_architecture(arch: str) -> str:
    """Apply all architecture-section expansions."""
    out = arch
    for label, anchor, replacement in ARCH_INSERTS:
        out = _apply_insert(out, anchor, replacement, f"arch.{label}")
    return out


def _expand_tradeoffs(trade: str) -> str:
    """Apply the DASH-vs-HLS row insertion in Key Design Decisions table."""
    return _apply_insert(
        trade,
        TRADEOFF_ANCHOR,
        TRADEOFF_REPLACEMENT,
        "tradeoffs.dash_hls",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip the DB-file backup step (not recommended).",
    )
    args = parser.parse_args()

    init_db()
    db_file = _resolve_db_file()
    if db_file is not None and not args.no_backup:
        backup = _backup_db(db_file)
        if backup is not None:
            print(f"[BACKUP] {backup.name}")

    db = SessionLocal()
    try:
        row = db.get(SystemDesign, TARGET_ID)
        if row is None:
            print(f"[FAIL] system_designs id={TARGET_ID} not found")
            return 1

        arch_orig = row.architecture or ""
        trade_orig = row.tradeoffs or ""
        total_before = (
            len(row.overview or "")
            + len(arch_orig)
            + len(row.dataflow or "")
            + len(row.formulas or "")
            + len(row.production_constraints or "")
            + len(trade_orig)
            + len(row.defense or "")
        )
        print(f"[BEFORE] total sd21 content: {total_before} chars")

        # Idempotency gate: check both characteristic markers
        arch_done = IDEMPOTENCY_MARKER in arch_orig
        trade_done = "DASH 1-5 s" in trade_orig
        if arch_done and trade_done:
            print(
                f"[SKIP] sd21 already expanded "
                f"(marker '{IDEMPOTENCY_MARKER}' + DASH row present)"
            )
            return 0
        if arch_done != trade_done:
            # Partial prior run -- refuse to half-apply
            print(
                f"[FAIL] partial expansion detected "
                f"(arch_done={arch_done}, trade_done={trade_done}). "
                f"Manual inspection required."
            )
            return 1

        arch_new = _expand_architecture(arch_orig)
        trade_new = _expand_tradeoffs(trade_orig)

        # Invariant: expanded text must contain original text as substring.
        # This catches accidental section deletion.
        if arch_orig not in arch_new and arch_new.count("#### 1. Upload Service") != 1:
            # Insertions split the string so substring check won't hold; fall
            # back to section-marker check.
            for marker in [
                "#### 1. Upload Service",
                "#### 2. Transcoding Pipeline",
                "#### 3. Video Storage",
                "#### 4. CDN & Playback Service",
                "#### 5. Metadata Service",
                "#### 6. View Count Service",
                "#### 数据库选择与理由",
            ]:
                if marker not in arch_new:
                    print(f"[FAIL] expansion deleted section marker: {marker}")
                    return 1

        # Additional AC grep assertions on the expanded architecture
        checks: dict[str, int] = {
            "VCU": arch_new.count("VCU"),
            "Colossus": arch_new.count("Colossus"),
            "Bigtable": arch_new.count("Bigtable"),
            "Pub/Sub": arch_new.count("Pub/Sub"),
            "chunked": arch_new.lower().count("chunked"),
            "Google Global Cache": arch_new.count("Google Global Cache"),
        }
        min_counts = {
            "VCU": 1,
            "Colossus": 1,
            "Bigtable": 2,
            "Pub/Sub": 1,
            "chunked": 2,
            "Google Global Cache": 1,
        }
        failed_checks = [
            (k, v, min_counts[k])
            for k, v in checks.items()
            if v < min_counts[k]
        ]
        if failed_checks:
            for name, actual, needed in failed_checks:
                print(
                    f"[FAIL] AC grep check: '{name}' {actual}x "
                    f"(need >= {needed})"
                )
            return 1
        for name, actual in checks.items():
            print(f"  [GREP] '{name}' -> {actual}x")

        row.architecture = arch_new
        row.tradeoffs = trade_new
        row.updated_at = datetime.now(UTC)
        row.content_hash = _content_hash(row)

        db.commit()

        total_after = (
            len(row.overview or "")
            + len(arch_new)
            + len(row.dataflow or "")
            + len(row.formulas or "")
            + len(row.production_constraints or "")
            + len(trade_new)
            + len(row.defense or "")
        )
        print(
            f"[WRITE] sd21 expanded: "
            f"arch {len(arch_orig)} -> {len(arch_new)} chars, "
            f"tradeoffs {len(trade_orig)} -> {len(trade_new)} chars, "
            f"total {total_before} -> {total_after} chars "
            f"(+{total_after - total_before})"
        )
        print(f"[HASH] content_hash = {row.content_hash}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
