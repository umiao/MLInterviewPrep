"""Fill verbal_outline + cheat_sheet for the 4 newest Meta interview SDs.

Targets (display_order 120-123, all currently NULL on these two columns):
  id=36 interview-harmful-content-detection
  id=37 interview-fb-post-privacy
  id=38 interview-spotify-audio-streaming
  id=39 interview-recommendation-system

Idempotent: overwrites the two columns it owns, leaves overview / architecture
/ dataflow / formulas / production_constraints / tradeoffs / defense untouched.

Style per project memory (feedback_content_style_cn_en):
  Chinese narration + English technical terms.
  verbal_outline: ~600-1000 chars, designed to be spoken in 2-3 minutes as
    the opening monologue at the start of a Meta SD interview.
  cheat_sheet: ~300-500 chars, last-minute flash card with top numbers and
    one-line decisions.
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

# ---------------------------------------------------------------------------
# Content (inline, bilingual CN narration + EN tech terms)
# ---------------------------------------------------------------------------

VERBAL_OUTLINES: dict[str, str] = {
    "interview-harmful-content-detection": """\
**口述脉络 (Verbal Outline) — 2-3 分钟开场**

先 clarify 三件事：scope 是 text + image + video 哪几种？规模量级（FB 是 5B+ posts/day）？延迟需求是 inline pre-publish 还是 async post-publish？基于这三个回答，我会把题目定义成一个 hybrid 系统：fast path 走 model serving 拦明显违规，slow path 走 human review 处理 borderline 内容。

**Architecture 一句话**：上游 Kafka topic 消费 user content → fast classifier (multi-modal, 100ms p99) → 若 confidence > 0.95 直接 block / shadow ban；否则进 review queue → 人工 + 二级 model → 终态写入 enforcement DB → 通知用户 + 上诉入口。

**核心 tradeoff**：precision vs recall 在不同 policy 下要分别配阈值（hate speech 偏 precision 防误杀，CSAM 偏 recall 即使误判也要拦）；fast path 用 distilled model 牺牲 1-2pp accuracy 换 10x throughput；human review 容量是瓶颈，靠 active learning 让模型挑最有学习价值的样本上 reviewer。

**Defense 关键 Q**：(1) 怎么处理新型 adversarial（如 OCR 文字嵌图）→ multi-modal fusion + 持续 retrain；(2) 跨 region policy 差异（GDPR vs 美国）→ rule engine 分 region 路由；(3) 如何衡量系统效果 → prevalence (% bad content shown / total impressions) + appeal rate。
""",

    "interview-fb-post-privacy": """\
**口述脉络 (Verbal Outline) — 2-3 分钟开场**

题目本质是 audience-visibility 计算：当 viewer V 看 Feed 时，对每条候选 post P，要回答"V 是否在 P 的可见受众里"。Meta 这题考的不是 ML，是 **access-control at scale** — 3B+ users × 100B+ posts，每次 Feed 加载要做几千次 visibility check，p99 < 5ms。

**Clarify**：privacy 模型是 Public / Friends / Custom List / Only Me 四级？还是要支持 negative exclusion (e.g. "Friends except X")？这个直接影响 storage cost。

**Architecture 一句话**：post 写时把 audience policy 物化成一个 **bitmap or set membership** 存到 hot store (Redis / TAO)；读时 viewer_id 进来用 O(1) 查表 + 二级过滤（block list, custom list）；celebrity post 有 fan-out write amplification 风险，靠 hybrid（read-side filter for celebs，write-side materialize for normal users）解决。

**核心 tradeoff**：write-side materialize（每条 post 算一次 audience，存好）— 读快但写贵 + storage 爆；read-side filter（读时算）— 写快但每次读慢；现实选 hybrid，按 author follower count 分流。

**Defense 关键 Q**：(1) 改 privacy 后老 audience cache 怎么更新 → CDC + Tombstone；(2) Custom List edit 怎么传播 → invalidation + lazy recompute；(3) 怎么 audit 历史泄露 → access log + replay。
""",

    "interview-spotify-audio-streaming": """\
**口述脉络 (Verbal Outline) — 2-3 分钟开场**

跟 video streaming 共享 CDN + ABR 框架，但 audio 有四个独立约束我会优先讲：(1) **3-tier codec ladder**（96/160/320 kbps Vorbis/AAC/HE-AAC），不像视频 6+ tier；(2) **gapless playback** — album 内连续两首曲子之间不能有 buffer gap，需要 prefetch + cross-fade；(3) **file-level DRM** 而不是 per-segment（audio 总长才几 MB，整文件加密成本可接受）；(4) **discovery 推荐** = CF (collaborative filtering) + audio embeddings (from raw waveform via CNN) 混合。

**Architecture 一句话**：upload → transcode 成 3 tier → S3 + Edge CDN (200+ POP) → client adaptive switch by bandwidth → 监听历史进 Kafka → 训练 two-tower (user / track embeddings) → 周更 Discover Weekly。

**核心 tradeoff**：offline download (premium feature) 跟 streaming-only 共享多少基础设施？我倾向 unified — download 就是 force highest tier + persistent cache，DRM 用同一套 license server。

**Defense 关键 Q**：(1) 新歌冷启动 → audio embedding 直接打 → 不依赖播放历史；(2) 怎么对抗刷量 → device fingerprint + listen-duration threshold（30s 才算一次有效播放）；(3) 全球 catalog 但 region 版权差异 → catalog-region join table 在 edge 缓存。
""",

    "interview-recommendation-system": """\
**口述脉络 (Verbal Outline) — 2-3 分钟开场**

我会按 **三阶段漏斗** 讲：召回 (Retrieval) → 排序 (Ranking) → 重排 (Re-ranking)。Meta 这种规模题（10B+ items × 3B users），关键是每阶段砍掉一个数量级，让最后 ranking 模型只看几百到几千候选。

**Stage 1 召回**：5-path multi-source — (a) two-tower DSSM embedding ANN (HNSW / Faiss IVF)，(b) user-item collab filtering，(c) graph-based (PinSAGE 风格)，(d) trending / fresh content，(e) follow-graph 直接召回。每路出 ~200，merge 去重剩 ~1000。**关键决策**：two-tower 必须 user / item 完全解耦，不允许 cross feature，不然没法 ANN。

**Stage 2 排序**：DLRM (Deep Learning Recommendation Model) backbone + MMoE (Multi-gate Mixture-of-Experts) 处理多目标 (CTR / 完播 / 收藏 / 评论 / D7 retention) + DCN-v2 (Deep & Cross Network) 学高阶交叉。Loss 多目标加权，权重靠线上 A/B 调。

**Stage 3 重排**：MMR (Maximal Marginal Relevance) 或 DPP (Determinantal Point Process) 做多样性，creator pacing 防同一作者刷屏，IPS (Inverse Propensity Score) 校正 position bias。

**Defense Q**：(1) two-tower 没 cross 怎么救 → ranking 阶段补；(2) MMoE expert 数量 → 4-8 个，等于目标数；(3) CTR↑ retention↓ → 上 D7-retention task 救；(4) GDPR explainability → 走 retrieval-source narrative，不解释具体打分。
""",
}

CHEAT_SHEETS: dict[str, str] = {
    "interview-harmful-content-detection": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 5B+ posts/day, 100ms p99 inline |
| Fast path 阈值 | confidence > 0.95 直接 block |
| Borderline 处理 | review queue + 人工 + 二级 model |
| Precision-Recall 策略 | hate-speech 偏 P，CSAM 偏 R |
| 模型 | distilled multi-modal (text+image+video) |
| Adversarial | OCR 文字嵌图 → multi-modal fusion |
| 度量 | prevalence (bad/total impressions) + appeal rate |
| Region | rule engine 分流 (GDPR vs US) |
| Active learning | reviewer 标 borderline 回馈 |
""",

    "interview-fb-post-privacy": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 3B users × 100B posts, p99 < 5ms 每条可见性 |
| Privacy levels | Public / Friends / Custom List / Only Me / Friends-except |
| Storage 策略 | hybrid: write-materialize for normal, read-filter for celeb |
| Hot store | Redis / TAO bitmap or set |
| Celebrity 阈值 | follower > 100K 走 read-filter |
| Audience update | CDC + Tombstone 异步刷 |
| Custom List edit | invalidation + lazy recompute |
| 写入路径 | post 到 audience materializer (Kafka) |
| Audit | access log + replay |
""",

    "interview-spotify-audio-streaming": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| Codec ladder | 96 / 160 / 320 kbps (3-tier，少于 video 6+) |
| 容器 | OGG Vorbis / AAC / HE-AAC |
| Gapless playback | prefetch 下一曲 + crossfade 50ms |
| DRM | file-level (而非 per-segment) |
| Discovery | CF + audio embedding (CNN on raw waveform) |
| ABR 决策窗口 | 4s buffer，缺则降 tier |
| CDN | 200+ POP edge cache |
| Offline download | force 320 kbps + persistent cache |
| Anti-fraud | device fingerprint + 30s 才算有效播放 |
| Region catalog | catalog-region join 在 edge 缓存 |
""",

    "interview-recommendation-system": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 漏斗 | Retrieval (10B->1K) → Ranking (1K->100) → Rerank (100->10) |
| Retrieval | 5-path: two-tower / CF / graph / trending / follow |
| Two-tower 模型 | DSSM, user-item 完全解耦, ANN via HNSW/Faiss-IVF |
| Ranking 模型 | DLRM + MMoE (4-8 expert) + DCN-v2 |
| 多目标 | CTR / 完播 / 收藏 / 评论 / D7 retention |
| Loss | 多任务加权，权重 A/B 调 |
| Rerank | MMR or DPP 多样性 + creator pacing + IPS 位置 bias |
| Cold start | item 走 content embedding，user 走 demographic prior |
| Online metrics | session length, D7 retention, post-CTR |
| Explainability | retrieval-source narrative (不解释打分) |
""",
}

TARGET_SLUGS = list(VERBAL_OUTLINES.keys())


def main() -> None:
    init_db()
    db = SessionLocal()
    chinese_pattern = re.compile(r"[一-鿿]")
    try:
        for slug in TARGET_SLUGS:
            row = db.query(SystemDesign).filter(SystemDesign.slug == slug).first()
            if row is None:
                print(f"[ERROR] slug not found: {slug}")
                continue

            v_new = VERBAL_OUTLINES[slug]
            c_new = CHEAT_SHEETS[slug]
            v_old = row.verbal_outline or ""
            c_old = row.cheat_sheet or ""

            v_action = "NOOP" if v_old == v_new else ("INSERT" if not v_old else "UPDATE")
            c_action = "NOOP" if c_old == c_new else ("INSERT" if not c_old else "UPDATE")

            row.verbal_outline = v_new
            row.cheat_sheet = c_new

            print(f"[{v_action}/{c_action}] {slug}: verbal={len(v_new)} cheat={len(c_new)}")

            for label, content in (("verbal", v_new), ("cheat", c_new)):
                if not chinese_pattern.search(content):
                    print(f"  [WARN] {label}: no Chinese chars!")

        db.commit()
        print("[DONE] verbal_outline + cheat_sheet patched for 4 Meta SDs.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
