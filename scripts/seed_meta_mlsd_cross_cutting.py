"""Seed Meta MLSD Cross-cutting 积木库 doc (T-P0-839).

Per T-P0-839 ([Meta-MLSD C]). Target: company_documents row for company_id=31
(Meta) titled '[Meta-MLSD] Cross-cutting 积木库 (drawer)'.

This is the cd:// drawer page reached from the Meta MLSD main hub (T-P0-832/840).
Content is the 9 跨题通用 ML 积木 — apply any one immediately when facing a new
recommendation / ranking / classification problem during the interview.

SOURCE:
  docs/prep/meta_mlsd_2026-05-11/source_02_family_taxonomy.md
    - Lines 4-6: 第二节 cross-cutting reusable pieces — 9 个积木 (积木 / 何时套用 /
                 一句 justification) inline format

DB TARGET: data/mle_prep.db, table=company_documents
  is_golden  = 0 (drawer page, NOT the default first page)
  doc_kind   = 'prep_note'
  source_type = 'manual'

Links:
  - sd://meta-reels-golden  → canonical 45-min walkthrough (T-P0-837, sd id=41)
  - cd://94                 → Family Taxonomy + 13 question cards (T-P0-838)

Idempotency: sentinel <!-- META_MLSD_CROSS_CUTTING_20260511 --> gates the write.
Second run = 0 writes when content is byte-identical.

Style:
  - Chinese narration + English ML terms (first-occurrence pattern)
  - 主表: 4-col markdown table (# | 积木 | 何时套用 | Justification)
  - Section 2: 9 H4 sub-headers, each 60-100 字 expanded note
  - Section 3: Decision Tree 60-80 字 if-else mapping
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- META_MLSD_CROSS_CUTTING_20260511 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta-MLSD] Cross-cutting 积木库 (drawer)"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"
IS_GOLDEN = 0

# Drawer doc id for Family Taxonomy (T-P0-838).
FAMILY_TAXONOMY_DOC_ID = 94

CONTENT = f"""{SENTINEL}

# Meta MLSD - Cross-cutting 积木库 (drawer)

> 9 个跨题通用的 ML 积木 — 题目变了, 积木不变. 记熟一次, 在 Meta MLSD 任意 rec/ranking/classification 题中可即时调用. 配套阅读: 13 题分型卡片 [cd://{FAMILY_TAXONOMY_DOC_ID}](cd://{FAMILY_TAXONOMY_DOC_ID}); 完整端到端示范 [sd://meta-reels-golden](sd://meta-reels-golden).

---

## 1. 积木总表 (9 piece quick-reference)

| # | 积木 | 何时套用 | Justification |
| - | --- | --- | --- |
| 1 | Two-tower retrieval + deep ranking | Standard rec/feed/search 默认架构 | retrieval 走 ANN, ranking 走 latency 富余下的 deep model |
| 2 | Multimodal embedding precomputed at upload | 内容为视频 / 图 / 音频 | 把内容理解开销跟 serving cost 解耦, 刷新只在 encoder 升级时 |
| 3 | Multi-task heads (engagement / quality / strong negative) | 任何 user feedback 非单一信号 | 单 binary label 损失信息; 多 head 还能 post-train tune 权重 |
| 4 | IPS / counterfactual replay | 任何讨论 exposure bias / A/B safety | offline 数据有 bias, replay 在 A/B 前过滤明显 broken candidate |
| 5 | Active exploration policy (onboarding + re-explore + content ramp) | 想 push 到 E5 信号 | 重构 exposure bias 为 data acquisition 问题 (高级 reframe) |
| 6 | LLM-as-teacher → distilled student | Label scarcity / 内容理解任务 | Teacher 离线 bulk inference, student 在线 serving (2025 Meta 实践) |
| 7 | Long-term holdout (~5% users, 30+ days) | 任何讨论 evaluation 完整性 | 短 A/B 抓不到 retention / filter bubble / fatigue |
| 8 | Calibration check across surfaces | 多 surface 混排或概率被下游消费 | 跨 head 的 score 不可比时 ranking 失真 |
| 9 | Slice metrics by confounder | 任何 evaluation 段 | aggregate 数字会掩盖 sub-group failure (duration / new vs return user) |

---

## 2. 9 积木 expanded notes

#### 积木 1. Two-tower retrieval + deep ranking

**何时套用**: rec / feed / search 默认两阶段架构. **要点**: retrieval 塔学 user / item embedding, ANN (HNSW / IVF) 召回 top-K (~1000); ranking 用 deeper cross / interaction network 在 latency 富余下排序. **Reels 应用** (见 [sd://meta-reels-golden](sd://meta-reels-golden)): two-tower 召回 + DLRM-style ranker 是 default skeleton, 不要在 retrieval 用全 cross feature.

#### 积木 2. Multimodal embedding precomputed at upload

**何时套用**: 内容 modality 是视频 / 图 / 音频时. **要点**: encoder 在 upload-time bulk 推, embedding 入 store; serving 路径只 lookup 不 re-encode. **解耦**: 内容理解开销 (heavy GPU) 跟 serving cost (low latency CPU) 分离. 刷新只在 encoder 升级时; 灰度 dual-write 双 embedding column 即可. Reels / IG 短视频默认.

#### 积木 3. Multi-task heads (engagement / quality / strong negative)

**何时套用**: 任何 user feedback 非单一信号的题. **要点**: 一个 shared backbone, 多 head 同时预测 click / like / share / complete / skip / hide. 单 binary label 信息损失大; 多 head 还能在 post-train 调权重做 surface / aging tradeoff. Reels final score = Σ w_k · p_k, 权重可 A/B test.

#### 积木 4. IPS / counterfactual replay

**何时套用**: 讨论 exposure bias / A/B safety / log-policy distribution shift 时. **要点**: log 内 propensity 已知 → IPS reweight; 否则学 propensity model. **Replay**: 用 logged data 重放新 policy, 比较 metric. **价值**: A/B 前过滤明显 broken candidate (e.g. ranker bug 让 quality 暴跌), 不烧 user traffic.

#### 积木 5. Active exploration policy (onboarding + re-explore + content ramp)

**何时套用**: 推 E5 信号 / 想突破 "exposure bias 是无解的" framing 时. **要点**: 把 exposure bias 重构为 **data acquisition problem** — 主动 explore 三个 budget: (a) onboarding 新用户 (b) re-explore 老用户 stale interest (c) content ramp 新 creator. 不是 randomness, 是 budget allocation.

#### 积木 6. LLM-as-teacher → distilled student

**何时套用**: label 稀缺 (manual annotation 贵) 或 content understanding 任务 (caption / topic / aspect). **要点**: LLM teacher 离线 bulk inference 生成 pseudo-label, student model 在线 serving. 2025 Meta 实践标配; ROI 在 teacher 调用一次产 1B 条 label, student 学完延迟 ~5ms.

#### 积木 7. Long-term holdout (~5% users, 30+ days)

**何时套用**: 讨论 evaluation 完整性时. **要点**: 短 A/B (1-2 周) 抓不到 retention / filter bubble / fatigue. 留 5% user 长期保留 (30-90 天) 跑对照, 测真实 long-term lift. **Trade-off**: 5% traffic 浪费 vs 避免 short-term metric 优化导致 long-term loss (e.g. 推 clickbait 短期点击涨, 长期 retention 跌).

#### 积木 8. Calibration check across surfaces

**何时套用**: 多 surface 混排 (Feed + Reels + Stories 一起排) 或概率被下游消费 (Ads bidding, notification gating). **要点**: 不同 head / 不同 surface 训出的 score 不可直接比. **诊断**: Expected Calibration Error (ECE) per surface; isotonic / Platt scaling 修正. Auction 场景必查.

#### 积木 9. Slice metrics by confounder

**何时套用**: 任何 evaluation 段. **要点**: aggregate AUC / NDCG 数字会掩盖 sub-group failure — duration bucket (short / mid / long video), new vs return user, country, device. **典型陷阱**: overall metric 涨 0.3%, 但 new user 跌 2% — total roll-out 会损失增长. 任何 readout 都报 slice.

---

## 3. 30 秒题型 → 积木 decision tree

- **rec / ranking / feed 类** (Q1 / Q4 / Q5 / Q6 / Q8 / Q9 / Q10 / Q11 / Q13): 默认套 1 + 3 + 4 + 5 + 7; 多 surface 加 8; 评估段加 9.
- **classification 类** (Q7 weapon ad): 套 6 (LLM teacher) + 7 + 9; 不要乱套 two-tower.
- **cold-start heavy 类** (Q5 events, 新 creator): 套 2 (precomputed embedding) + 5 (active exploration); cold-start 不是 ranking 问题, 是 data 问题.
- **graph 类** (Q3 friend rec): 1 不套 — graph traversal 取代 two-tower; 4 / 7 / 9 仍套.
- **prediction-as-feature 类** (Q12 event attendance): 先问 downstream consumer; 套 8 (calibration) 比套 ranking architecture 重要.

→ 配套 13 题卡片 [cd://{FAMILY_TAXONOMY_DOC_ID}](cd://{FAMILY_TAXONOMY_DOC_ID}); 端到端示范 [sd://meta-reels-golden](sd://meta-reels-golden).
"""


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_content(content: str) -> None:
    """Cheap structural checks on the content payload (mirrors task spec AC)."""
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing")

    # AC #2: length 3000-5500 chars per task spec.
    n = len(content)
    if not (3000 <= n <= 5500):
        raise RuntimeError(f"content length {n} not in [3000, 5500]")

    # Section markers
    for marker in (
        "# Meta MLSD - Cross-cutting 积木库",
        "## 1. 积木总表",
        "## 2. 9 积木 expanded notes",
        "## 3. 30 秒题型",
    ):
        if marker not in content:
            raise RuntimeError(f"section marker missing: {marker!r}")

    # AC #4: 5 keyword spotcheck.
    for kw in (
        "Two-tower retrieval",
        "IPS",
        "LLM-as-teacher",
        "Long-term holdout",
        "Slice metrics",
    ):
        if kw not in content:
            raise RuntimeError(f"keyword spotcheck missing: {kw!r}")

    # AC #3: main markdown table = header + sep + 9 data rows >= 11 lines starting with '|'.
    table_lines = [
        ln for ln in content.splitlines()
        if ln.lstrip().startswith("|")
    ]
    if len(table_lines) < 11:
        raise RuntimeError(
            f"main table too short: {len(table_lines)} lines starting with '|'; "
            f"need >=11 (header + sep + 9 data rows)"
        )
    # Explicit: 9 numbered rows '| 1 |' .. '| 9 |' in Section 1.
    for i in range(1, 10):
        if f"| {i} |" not in content:
            raise RuntimeError(f"main table row '| {i} |' missing")

    # AC #5: at least one sd://meta-reels-golden link OR cd:// link.
    if "sd://meta-reels-golden" not in content and "cd://" not in content:
        raise RuntimeError("need at least one sd://meta-reels-golden or cd:// link")
    # In practice we have both:
    if "sd://meta-reels-golden" not in content:
        raise RuntimeError("sd://meta-reels-golden link missing")
    if f"cd://{FAMILY_TAXONOMY_DOC_ID}" not in content:
        raise RuntimeError(
            f"cd://{FAMILY_TAXONOMY_DOC_ID} (family taxonomy backlink) missing"
        )

    # 9 '#### 积木' headers — one per piece.
    piece_headers = sum(
        1
        for i in range(1, 10)
        if f"#### 积木 {i}." in content
    )
    if piece_headers != 9:
        raise RuntimeError(
            f"expected 9 '#### 积木 N.' headers, got {piece_headers}"
        )


def main() -> int:
    """Upsert the Meta MLSD Cross-cutting 积木库 doc (idempotent)."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    validate_content(CONTENT)
    print(f"[OK] content validated: len={len(CONTENT)}")

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT name FROM companies WHERE id = ?", (COMPANY_ID,)
        ).fetchone()
        if row is None:
            print(f"[ERROR] company_id={COMPANY_ID} not found")
            return 1
        print(f"[OK] target company: id={COMPANY_ID} name={row[0]!r}")

        # Verify the family taxonomy doc id is still valid (defensive guard
        # against drift if the row gets deleted/re-inserted at a new id).
        ft = conn.execute(
            "SELECT title FROM company_documents WHERE id = ?",
            (FAMILY_TAXONOMY_DOC_ID,),
        ).fetchone()
        if ft is None or "Family Taxonomy" not in ft[0]:
            print(
                f"[WARN] cd://{FAMILY_TAXONOMY_DOC_ID} backlink may be stale: "
                f"id={FAMILY_TAXONOMY_DOC_ID} row={ft!r}"
            )

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
                "is_golden, content_hash, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    COMPANY_ID,
                    DOC_TITLE,
                    CONTENT,
                    SOURCE_TYPE,
                    DOC_KIND,
                    IS_GOLDEN,
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
