"""Seed: T-P0-837 [Meta-MLSD A] Reels Golden Example -> system_designs.

INSERTs (or idempotently updates) the canonical Meta MLSD golden example as
``system_designs(slug='meta-reels-golden')``, drawer-reachable via
``sd://meta-reels-golden``. Sourced verbatim from
``docs/prep/meta_mlsd_2026-05-11/source_01_pacing_golden.md`` (lines 1-362)
which is the user's own pacing/timing/strong-moment playbook for Reels Home
Feed Recommendation.

Target row shape (9 prose columns, all non-NULL, each > 200 chars; total
content > 8000 bytes):
  - overview                : pacing philosophy + 4 strong moment 预分配 + ML-native vocab
  - architecture            : 2-stage retrieval+ranking + multi-channel + DLRM + multimodal
  - dataflow                : 8-segment 0-5 / 5-12 / 12-18 / 18-26 / 26-32 / 32-38 / 38-42 / 42-45 minute-by-minute narrative
  - formulas                : label schema (watch ratio, strong+, early-skip, ambiguous middle), loss weighting (Pareto)
  - production_constraints  : multimodal precompute, quarterly refresh, async candidate, feature freshness策略
  - tradeoffs               : pretrained-vs-scratch, IPS-vs-exploration, watch-ratio-vs-retention, compliance-as-filter
  - defense                 : 4 strong moment 完整英文台词 verbatim (Moments #1-#4)
  - verbal_outline          : key verbal patterns + drift-recovery 句式 + ML-native YES/NO 对照表
  - cheat_sheet             : 元结构一图概览 + 8 条偏好节奏 meta-rules

Idempotent: re-running upserts in place by `slug`. Sentinel-based UPSERT
keyed on `slug='meta-reels-golden'`.

Usage::

    python scripts/seed_meta_reels_golden_sd.py [--db data/mle_prep.db] [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

SLUG = "meta-reels-golden"
TITLE = "Meta MLSD Golden Example: Reels Home Feed Recommendation (45min walkthrough)"
SUBTITLE = (
    "Meta MLSD Golden Example — canonical pacing + 4 strong moments + production-aware 英文台词. "
    "适用于 Reels / Feed / Notification / Friend-rec / Ads 等 Meta MLSD 题型 (80% 结构复用). "
    "Reference back via cd://<Meta hub doc id> 由 T-P0-832 hub 反向链接."
)
DISPLAY_ORDER = 130
SOURCE_PATH = "docs/prep/meta_mlsd_2026-05-11/source_01_pacing_golden.md"


OVERVIEW = """\
# Reels Home Feed Recommendation — 45min Golden Walkthrough

## 整体节奏哲学

**前 5 分钟独裁式 framing**：60-90 秒说完一个完整 proposal（2 specialty thesis 各 45-60s），不问 QPS / SLA / surface 维度。结尾用 yes/no question 收尾 (`"Does this make sense, or is there a different angle you'd like me to anchor on?"`)，等面试官点头就立刻往下推。

**中段 30 分钟你主导但邀请方向**：每个 body 段开场先 announce sub-structure (`"Let me walk through this in N parts: A, B, C"`)，列完 bullets 立刻 pick 1 expand 60 秒，每 8-10 分钟主动 zoom-out 或邀请面试官选 deepening 方向 (`"Want me to deepen retrieval, ranking, or the multi-task heads?"`)。

**最后 10 分钟主动 zoom-out**：35-40 min 强制做一次 top-N risks summary（这是 E5 边界 signal，也是 E4 strong 必备），serving 段刻意短 (`"I won't go deeper unless you'd like"` = graceful exit deprioritize signal)，余下做 Q&A。

## 4 个 strong moment 预分配（不要临场决定）

固定位置投放，每个 strong moment 必须包含 **reframe / claim → 3 concrete actions with quantification → failure modes → trade-off articulation**：

| # | Time   | Theme                                  | Hook                                                                         |
|---|--------|----------------------------------------|------------------------------------------------------------------------------|
| 1 | 0-5    | Multimodal lifecycle (framing)         | pretrained backbone + fine-tune + upload-time compute + quarterly refresh    |
| 2 | 5-12   | Label schema (data section)            | multi-head (watch ratio + strong+ / early-skip) + ambiguous middle + duration confounder |
| 3 | 26-32  | Exposure bias reframe (bias section)   | data acquisition policy NOT just IPS — onboarding + re-explore + cold ramp   |
| 4 | 38-42  | Zoom-out (before serving section)      | 3-sentence summary + top 3 risks (each with mechanism + alarm signal)        |

## ML-native vocabulary only

**下意识审查每一句话**。Infra 词汇只在面试官主动问 serving 时才出现：

| YES (ML-native, 主动用)                                                       | NO (infra-only, 被动用)                                  |
|--------------------------------------------------------------------------------|----------------------------------------------------------|
| model class / label / feature / bias / objective / evaluation                  | SLA / NFR / FR / QPS                                     |
| freshness / drift / calibration                                                | read/write ratio / service / API / cache / network       |
| retrieval / ranking / re-ranking / multi-task heads / shared backbone          | availability / fan-out / replication factor              |
| exposure bias / propensity / IPS / counterfactual replay / long-term holdout   | partition / sharding / quorum                            |

## E4 not E5 — 边界提醒

不要 invent novel methods，不要 over-scope ("2 years out we'd...")。要的是 **confident execution of standard playbook + 1-2 deeper insights**。每个决策点说出 "我选 A 因为 X，代价是 Y，如果 Z 变化我会切到 B"。
"""


ARCHITECTURE = """\
# Architecture: Two-Stage Retrieval + Ranking + Multimodal Embedding Lifecycle

## 顶层结构 (canonical 2-stage funnel)

```
[Multimodal Content Embedding Pipeline]  -- upload-time, quarterly encoder refresh
        │
        ▼ (precomputed content embedding, cached in index)
[Retrieval — multi-channel, 60/20/20]
        ├── (a) Personalized two-tower (60%)   — main personalization channel
        ├── (b) Trending / recency (20%)        — fresh content with limited history
        └── (c) Diversity (20%)                 — under-represented content clusters
              │
              ▼ (~1000 candidates per request)
[Ranking — DLRM-style multi-task]
        ├── sparse-feature embeddings + dense-feature MLP
        ├── deep cross network for feature interactions
        ├── (optional) transformer / GRU over last-K session items
        └── multi-task heads → weighted combine (post-train tunable)
              │
              ▼ (~50-100 items, tunable score)
[Re-ranking / Hard Filters]
        ├── compliance / safety hard filter (NOT soft loss term — category error)
        ├── creator-side pacing / diversity dedup
        └── final ordered list returned
```

## 1. Multimodal Embedding Pipeline (upload-time, decoupled)

- **Visual encoder**：pretrained video encoder (ViViT / TimeSformer 类) over frame sequences；fine-tune on Reels-specific contrastive objective (co-engaged videos as positives)
- **Audio encoder**：pretrained audio encoder over soundtrack (Wav2Vec2 / VGGish)；soundtrack 是 trending 信号的重要载体
- **Text encoder**：lightweight BERT over caption / hashtag / OCR-extracted overlays (大多数 Reels text 极少)
- **Fusion**：concat + projection MLP → single content embedding (e.g., 256-dim)
- **Refresh cadence**：encoder 权重 **quarterly** 重训 + 重算所有 content embedding；single-video embedding compute 只在 upload-time 一次，**decouples content understanding cost from serving cost**

## 2. Retrieval — Multi-Channel Two-Tower

- **(a) Personalized two-tower (60%)**：user tower (long-term profile + recent session history)、content tower (multimodal embedding + content metadata)；ANN (Approximate Nearest Neighbor 索引，**HNSW** = Hierarchical Navigable Small World / **ScaNN** = Scalable Closest Neighbor Search) over content index；contrastive training，negatives = in-batch + hard negatives mined from early-skip events
- **(b) Trending / recency channel (20%)**：surface fresh content with limited engagement history；按 upload time bucket + 早期 engagement velocity 召回
- **(c) Diversity channel (20%)**：pull from under-represented content clusters relative to the user's recent N sessions；这是 bias mitigation 的 retrieval-layer 投影

## 3. Ranking — DLRM-style multi-task

- **Sparse + dense + cross**：sparse feature embeddings → MLP，dense features → MLP，**deep cross network** for explicit feature interactions
- **Multi-task heads**：watch-ratio head / explicit-engagement head / early-skip head；**shared backbone** + head-specific top layers (watch-ratio 与 engagement correlated 足够 benefit from sharing)
- **Session-aware module (optional)**：transformer 或 GRU layer over last K items in current session → 输出 session-context embedding 喂回 ranking model（这是 Reels 区别于 Feed 的关键 — 主要 lever 是 within-session fatigue 和 drift）
- **Score combine**：final score = Σ w_k · p_k(head)，**weights post-train tunable**（无需 retrain 即可调 engagement-vs-quality trade-off）

## 4. Re-ranking — Hard Filters + Business Logic

- **Compliance / safety**：作为 **hard filter** at re-ranking（NOT soft loss term）— compliance violation 不是 "less engagement"，是 disqualifying；treating it as soft loss 是 **category error**
- **Creator-side pacing**：避免 single creator 在 session 内 over-exposed
- **Diversity dedup**：MMR / DPP-style 在 final list level

## 5. Serving (deliberately light, only if asked)

- **ANN-based retrieval** over content index → ~1000 candidates
- **Multimodal embeddings precomputed at upload**，serving-time content cost minimal
- **User-side features fresh at request**，content-side features cached（content state 变化慢于 user state）
- **Async candidate pre-compute** for active users during predictable idle windows，refresh ranking at request time

## ML-native diverges 的关键点（区别于通用 ranking system）

1. **Multimodal lifecycle**: upload-time encoding + quarterly refresh，不是 request-time encoder call
2. **Session-aware (NOT just user-aware)**: Reels 是 session-based continuous consumption，within-session features 必须 request-time 计算
3. **Multi-channel retrieval**: 单一 two-tower 不够，trending + diversity 是 bias mitigation 的 first-line
4. **Multi-task with post-train weights**: weights 不写死在 loss 里，是 production tunable lever
"""


DATAFLOW = """\
# Dataflow: 45min 八段时间表 (minute-by-minute narrative)

## 0-5 min · Framing  ← Strong Moment #1

**开场 declarative (60-90s)**：

> "I'll frame this as a recommendation system for Reels in the home feed, with retrieval plus ranking as the core structure. There are **two intrinsic specialties** of this problem that will drive most of my design decisions, and I want to put them on the table upfront."

**Specialty 1 — Multimodal lifecycle (Strong Moment #1 投放此处)**：

> "First, Reels are short-form videos, which means content understanding cannot rely on metadata or text alone. Most Reels are UGC with minimal text, and trends are visual or audio-driven. So I'd compute multimodal embeddings — a pretrained video encoder for visual frames, an audio encoder for soundtracks, and a text encoder for any captions — fused into a single content embedding **computed once at upload time**. I'd start with pretrained backbones and fine-tune on a Reels-specific contrastive objective, where co-engaged videos are positives. The embedding gets refreshed only when we improve the encoder, **roughly quarterly**. This **decouples content understanding cost from serving cost**."

**Specialty 2 — Session dynamics**：

> "Second, Reels consumption is session-based and continuous. Unlike a structured feed where a user picks one item, Reels users consume tens of videos sequentially. This creates within-session dynamics — diversity collapse, fatigue, interest drift — that we have to model explicitly. The implication is that we need **within-session features computed at request time**, not just batch user profiles, and our ranking model needs to be **session-aware not just user-aware**."

**Active deprioritize + yes/no close**：

> "I'm choosing not to deep-dive on cold-start, content moderation, or multi-resolution storage for now, but I'll flag them as risks later. Does this framing make sense, or is there a different angle you'd like me to anchor on?"

---

## 5-12 min · Data & Labels  ← Strong Moment #2

**Announce structure (3 parts)**：

> "Let me walk through this in three parts: data sources, label schema, and biases. I'll **start with labels** since they're the most non-trivial for Reels."

**Data sources (30s, fast list)**：impression logs / engagement logs (watch time, likes, comments, shares, follows, swipe events) / content metadata (uploader, duration, embeddings, hashtags) / user-side data (long-term profile, recent session history, demographics).

**Label schema (Strong Moment #2 投放此处)** — see `formulas` column for full schema.

**Bias preview (transition)**：

> "I'll come back to biases in a moment when we discuss exploration — but at the data layer, the **dominant risk is that all our labels are conditioned on what we chose to show**. Let me hold that thought and move to features unless you want to deepen labels first."

---

## 12-18 min · Features  (节奏要快, 不是 strong moment 区)

**4 buckets (10s announce → expand 1)**：

1. **User features**: long-term profile embedding (learned from past engagement), demographic, recent topic exposure (last N sessions)
2. **Content features**: the multimodal embedding, uploader features, duration, recency, historical engagement statistics
3. **Context features**: time of day, device, network type, **session position** (how many Reels in this session so far)
4. **Cross features**: user-content historical interaction (has user followed uploader? engaged with similar content recently?)

**Expand session-context features (40s)**：

> "The non-trivial design choice here is **session-context features** — 'topic exposure in the last 5 items in this session', 'average watch ratio so far this session', 'swipe rate this session'. These have to be **computed at request time**, not pre-aggregated. They're the main lever for handling within-session fatigue and drift."

**Trade-off statement**：fresh user features (request-time) vs precomputed content features (cached)。

---

## 18-26 min · Model Architecture  (邀请面试官选 deepening)

**Two-stage announcement (1 min)**：retrieval + ranking。

**Retrieval (90s)**：two-tower (user tower + content tower) + ANN，contrastive training，negatives = in-batch + hard negatives from early-skip。

**Multi-channel detail (60s)** — **量化比例 60/20/20**：

> "I'd actually run **multiple retrieval channels in parallel**: (1) the main two-tower personalized channel, (2) a trending/recency channel that surfaces fresh content with limited history, (3) a diversity channel that pulls from under-represented content clusters relative to the user's recent history. Each channel contributes a fraction of the candidate pool — maybe 60/20/20."

**Ranking (90s)**：DLRM-style sparse/dense towers + deep cross network + multi-task heads → weighted combine (post-train tunable)。

**Invite deepening (key collaborative-mode signal)**：

> "Want me to deepen retrieval, ranking architecture, or the multi-task head design?"

**If they pick ranking** — deepen with (a) sharing strategy (shared backbone + head-specific top layers), (b) Pareto-style loss weighting NOT gradient-based balancing, (c) sequence modeling (transformer / GRU over last K items)。

---

## 26-32 min · Bias & Objectives  ← Strong Moment #3

**Setup (30s)**：

> "I want to spend time here because I think **bias handling is where most recommendation systems underinvest**."

**Standard correction (30s)** — IPS / propensity weighting at training time — **作为铺垫**。

**Strong Moment #3 核心 (90s)** — reframe exposure bias as data acquisition problem，三层 intervention (onboarding labeled exploration / periodic re-explore 5% budget / content-side cold-start ramp)，failure modes，"this is a stronger lever than IPS"。see `defense` column for verbatim 台词。

**Objectives (60s)**：3 components combined — user engagement (multi-head) / ecosystem value (creator retention, diversity) / **compliance as hard filter NOT soft loss term** (category error)。

---

## 32-38 min · Evaluation

**3 layers (offline / online / long-term)**：

- **Offline (60s)**: per-head metrics first — NDCG and weighted watch ratio for engagement head, AUC for explicit engagement and early-skip。然后 aggregate ranking metrics — session-level diversity, coverage of long-tail content。**Critically**: all metrics sliced by **video duration buckets** (confounder) AND by user segment (new vs established)。
- **Counterfactual replay (30s)**: before A/B，logged data with IPS-weighted replay estimates online performance，catches obviously broken candidates。
- **Online A/B (40s)**: **session-level metrics not item-level** — session length, return rate, day-N retention。
- **Long-term holdout (40s)**: 30+ day holdout for filter bubble narrowing, creator ecosystem effects, fatigue accumulation。

**Final flag (senior signal)**：

> "One thing I want to flag: the **alignment problem between offline and online**. Offline NDCG improvements don't always translate to online retention. I'd track this correlation explicitly and recalibrate offline metrics when they drift from online outcomes."

---

## 38-42 min · Zoom-out + Top Risks  ← Strong Moment #4

**3-sentence summary** + **top 3 risks** (each with mechanism + alarm signal) + **invite deepening** — see `defense` column for verbatim 台词。

---

## 42-45 min · Serving (light) + Q&A

**Deliberately short (2 min max)**：

> "On serving, two-stage matches our two-stage model: ANN-based retrieval over the content index returns ~1000 candidates, ranking scores them with the deep model. Multimodal embeddings are precomputed at upload, so serving-time content cost is minimal. User-side features computed at request, content-side features cached. We can precompute a candidate pool for active users during predictable idle windows and refresh at request time with fresh ranking. **I won't go deeper unless you'd like** — happy to discuss monitoring or rollback if useful."

**Purpose of brevity**: 主动 deprioritize = 告诉面试官你 aware of serving 但不在 ML SD round 上花预算。Graceful exit signal。
"""


FORMULAS = """\
# Label Schema (Strong Moment #2 核心) + Loss Weighting

## Multi-head label schema (Reels 区别于 standard ranking 的关键)

> "Label 1: **normalized watch ratio**, defined as `watch_time / video_duration`, capped at 1.0. Critical to normalize — raw watch time would systematically over-weight long content. A 3-second video watched fully should count as much as a 60-second video watched fully."

> "Label 2: **strong positive (binary)** — explicit engagement: like, comment, share, follow, save. Sparse but high-precision."

> "Label 3: **strong negative (binary)** — early swipe-away, defined as user swiping within the **first 2-3 seconds or before 20% completion**. This is the implicit hard-negative signal that's unique to Reels and crucial for breaking exposure bias in negative sampling."

### 关键 nuance: ambiguous middle

> "A user who watches 50% then swipes is genuinely ambiguous — not a hard negative, not a strong positive. I'd treat it as **weakly positive on the watch-ratio head and exclude it entirely from the early-skip head**. Forcing a binary label on ambiguous data adds noise."

### 公式定义

| Label | 定义 | Head type | Notes |
|-------|------|-----------|-------|
| `watch_ratio` | `min(watch_time / video_duration, 1.0)` | regression (or bucketed classification) | 主要 engagement 信号；duration confounder must be sliced |
| `strong_positive` | `1 if {like ∨ comment ∨ share ∨ follow ∨ save} else 0` | binary classification | sparse high-precision，类别 imbalance 严重 |
| `early_skip` | `1 if (swipe_at < 2.5s ∨ watch_ratio < 0.2) else 0` | binary classification | implicit hard-negative；exclude ambiguous middle (0.2 ≤ watch_ratio ≤ 0.5) |

### Duration confounder

> "**Video duration is a confounder for almost every engagement label**. A 5-second loop is much easier to complete than a 60-second clip. So duration becomes both a **feature input** AND an **evaluation slice** — we should be looking at metrics conditioned on duration buckets, not just aggregate."

Duration buckets 建议: `[0-5s, 5-15s, 15-30s, 30-60s, 60s+]`，offline metrics 必须分 bucket report。

## Loss weighting (Strong Moment ranking-deep 投放)

**Combination strategy**:

```
final_score = w_1 · p̂_watch_ratio + w_2 · p̂_strong_positive + w_3 · p̂_early_skip_inverse
```

其中:
- 权重 `w_k` **post-train tunable** — 可调 engagement-vs-quality trade-off 而无需 retrain
- `p̂_early_skip_inverse = 1 - p̂_early_skip`，所以高 score = unlikely early skip

### Tuning approach (senior signal)

> "I'd start with **equal weighting** and tune via **Pareto-style search on offline metrics**, NOT gradient-based loss balancing — it's more interpretable and the heads aren't competitive enough to require sophisticated balancing."

**Why not GradNorm / uncertainty weighting**: 解释性差，head 之间不强 competitive (shared backbone 已经 absorb 大部分 correlation)，Pareto search on offline metrics 更可 audit、更易 ship review。

### Sharing strategy

> "Shared backbone, head-specific top layers. Watch-ratio and engagement are **correlated enough to benefit from shared representation**."

```
[shared backbone (sparse-emb + dense-MLP + DCN)]
        │
        ├─── [head 1: watch_ratio top-MLP]    (regression)
        ├─── [head 2: strong_positive top-MLP] (binary)
        └─── [head 3: early_skip top-MLP]      (binary)
```

## Calibration (cross-surface mix 时关键)

如果 final 系统要 mix push / in-app / email surfaces，每个 head 输出必须 probability-calibrated (isotonic 或 Platt scaling on a held-out slice)，否则不同 surface 的 score 不可直接比较。Reels home feed 单 surface 通常不需要严格 calibration，但 follow-up 问 cross-surface 时 surface 即可 +1 senior signal。

## 一句话总结

**Multi-head 不是 nice-to-have，是 Reels 的 ML 内核**。watch ratio 单 label 会被 long-content / clickbait gaming；strong positive 单 label 太 sparse 学不出；early skip 单 label 退化成 spam filter。三 head 互补是 Reels MLSD 的 ML-depth 投影面。
"""


PRODUCTION_CONSTRAINTS = """\
# Production Constraints (ML-side, not infra-side)

## 1. Multimodal embedding 生命周期

- **Compute timing**: encoder forward pass **only at upload time** (一次性 cost per video) — 不是 request-time
- **Refresh cadence**: encoder 权重 **quarterly** 重训，全库 content embedding **quarterly batch refresh**
- **Cost decoupling**: 把 content understanding 的 GPU cost 从 serving path 中剥离，serving 看到的只是 lookup-by-id 拿 precomputed vector

> "This decouples content understanding cost from serving cost."

## 2. Feature freshness 策略 (asymmetric)

| Side | Freshness | Reason |
|------|-----------|--------|
| User-side features | **fresh at request time** | user state 变化快 (session-context features 是 main lever for fatigue / drift) |
| Content-side features | **cached / precomputed** | content state 变化慢，per-request recompute 浪费 |

> "Fresh user features versus stale precomputed features. For Reels I'd compute user-side features fresh at request, but content-side features can be precomputed and cached."

## 3. Candidate precompute (async, idle-window)

- **Active users**: precompute candidate pool during predictable idle windows (e.g., overnight 用户低活跃期)
- **Refresh at request time**: 拿 precomputed pool + fresh user-side features 重 rank
- **New / sporadic users**: fall through to full retrieval pipeline at request time

## 4. Exploration budget as production constraint

5% per-session impression budget for controlled exploration (Strong Moment #3 的 production 投影):
- **Capped per session** — 避免 UX degradation
- **Quality eligibility filter** — 避免 low-quality content 套利 exploration budget
- **Wider candidate pool than production retrieval** — 否则 exploration data 还是 biased (production retrieval 已经过滤掉 long-tail)

## 5. Compliance / safety as hard filter (NOT soft loss)

- **位置**: re-ranking 层 hard filter，不是 loss term
- **为什么**: compliance 不是 "less engagement"，是 **disqualifying**
- **Cost**: 单独 compliance classifier pipeline (可能是独立的 LLM-finetune 系列 model)，结果作 binary mask

> "Treating compliance as a soft loss term is a category error that recommendation teams often make."

## 6. Long-term holdout (30+ days)

- 一小撮用户 hold out 不接收新模型 launches，**at least 30 days**
- **目的**: 捕捉短 A/B 看不到的 long-term degradation — filter bubble narrowing, creator ecosystem effects, fatigue accumulation
- **Cost**: 这撮用户上不了新 feature，需要 product 同意 trade business loss for 风险 detection

## 7. Production scar (E4 senior signal — 1-2 个就够)

可以 surface 类似:

- "In my past work, we found that **adding more features beyond ~200 actually hurt** because the model overfit to training distribution shifts. So I'd start with a focused feature set and validate freshness/coverage before expanding."
- "For ranking with a deep model, I'd actually **keep scoring on one node per request rather than distribute** — the network cost of feature shipping usually outweighs the compute savings."
- "Training-serving skew is a real risk — we need to log not just clicks but also impressions and **the features at serving time**, because that's the only way to verify offline-online consistency. The logging volume is non-trivial — if storage becomes a constraint, I'd sample negatives rather than reduce features."

## 不要主动展开的 infra 词汇

QPS / SLA / availability / replication / sharding / fan-out / cache TTL / network bandwidth — 这些是 infra round 词汇，**ML SD round 主动用就被 down-leveled**。被问到再用。
"""


TRADEOFFS = """\
# Tradeoffs (每个决策点必须 surface, "I pick A because X, costs Y, switches to B if Z")

## 1. Pretrained backbone + fine-tune  vs  from scratch

**Pick**: pretrained backbone + Reels-specific contrastive fine-tune。

| | Pretrained + fine-tune (pick) | From scratch |
|---|---|---|
| Data efficiency | 高 — backbone 已 absorb 大量 visual / audio prior | 低 — 需要 100x 标注数据 |
| Compute cost | 低 — 只 fine-tune top layers + lightweight pretrain refresh | 高 — full encoder training cycle |
| Domain alignment | 中 — pretrain domain 可能与 Reels 不完全重合 | 高 — 但 ROI 低于 fine-tune |
| **Why pick**: cost decoupling 的 enabler — quarterly encoder refresh 是 fine-tune 的，不是 full retrain，所以可行 |

## 2. IPS / propensity weighting  vs  active exploration policy

**Pick (Strong Moment #3 core claim)**: 把 exposure bias **reframe as data acquisition problem**，IPS 作为铺垫但不是 main lever。

| | IPS / Propensity weighting | Active exploration (pick as primary) |
|---|---|---|
| Lever type | **Data correction** — 调整 you have 的 data | **Data acquisition** — 改变 you collect 的 data |
| Implementation | training-time loss reweighting | system-level (onboarding + 5% budget + cold-start ramp) |
| Cost | 单 ML team 即可 ship | **Cross-functional cost** — product + growth 也要参与 |
| Ceiling | 受限于 historical retrieval 的 candidate pool | 可以扩张 candidate pool 本身 |
| **Why pick**: "**It's a stronger lever, but it requires cross-functional cost — product and growth pay part of the bill that ML would otherwise pay in accuracy loss**" |

## 3. Watch-ratio optimization  vs  long-term retention

**Pick**: multi-head 主优化 + long-term holdout 防御。

| | Watch-ratio 主优化 (pick) | Retention 主优化 |
|---|---|---|
| Signal density | 高 — 每 impression 都有 watch ratio | 低 — retention 是 cohort-level 信号 |
| Reward latency | 立刻 | 30+ 天 |
| Failure mode | **Clickbait / rage content gaming** | data sparsity，模型欠拟合 |
| Defense | long-term holdout + explicit-engagement head + creator quality survey | N/A (没有 short-term signal 可 defend) |
| **Switching trigger**: "If we ever see watch ratio going up but retention going down, that's the most important alarm" |

## 4. Compliance as hard filter  vs  compliance as loss term

**Pick (firm claim)**: hard filter at re-ranking。

| | Hard filter (pick) | Soft loss term |
|---|---|---|
| Semantic correctness | Compliance violation = disqualifying | Compliance violation = "less engagement" |
| Audit-ability | 高 — 是 / 否 binary outcome | 低 — 与 score 混在一起 |
| Failure mode if混 | 高 engagement 内容可能 override 轻度 compliance issue | clean |
| **Category claim**: "**Treating compliance as a soft loss term is a category error**" |

## 5. Shared backbone + head-specific top  vs  separate models

**Pick**: shared backbone + head-specific top layers (3 heads)。

| | Shared backbone (pick) | Separate models per head |
|---|---|---|
| Parameter efficiency | 高 | 低 |
| Negative transfer risk | 中 — heads correlated 时 minor | N/A |
| Head correlation | **Benefits from sharing** (watch-ratio ↔ explicit engagement correlated) | 不利用 correlation |
| Calibration drift | 较易 (joint train) | 各 head 独立漂移 |
| **Why pick**: "Watch-ratio and engagement are correlated enough to benefit from shared representation" |

## 6. Pareto-search loss weighting  vs  GradNorm / Uncertainty weighting

**Pick**: Pareto search on offline metrics post-train。

| | Pareto search (pick) | GradNorm / Uncertainty |
|---|---|---|
| Interpretability | 高 — 可看到 frontier 上 trade-off | 低 — 隐式权重 |
| Audit | 易 ship-review | 难 ship-review |
| Retraining cost | 0 — post-train tuning | 需要 retrain |
| Best for | heads not strongly competitive (Reels 情况) | heads strongly competitive |

## 7. Multi-channel retrieval (60/20/20)  vs  single channel

**Pick**: 3-channel parallel — personalized 60% / trending 20% / diversity 20%。

| | Multi-channel (pick) | Single two-tower |
|---|---|---|
| Cold start (content-side) | Trending channel handles | 需要专门 cold-start logic |
| Exploration | Diversity channel built-in | 需要 IPS / 上层 exploration policy |
| Filter bubble | 显著 mitigation | 严重 |
| Coverage of long-tail | 高 | 低 |
| **Cost**: 3 个 retrieval index 维护 + candidate pool budget 分配 — 但与 mitigation 收益相比划算 |

## 8. Within-session features fresh  vs  pre-aggregated batch

**Pick**: within-session features **request-time**。

| | Request-time fresh (pick) | Pre-aggregated batch |
|---|---|---|
| Use case fit | 唯一可行 — session 只有几分钟 | 不可行 (session 没结束) |
| Compute cost | 高 — 每 request 算 | 低 — batch |
| **Why no choice**: Reels 的 within-session dynamics 是 ML 内核，pre-agg 直接不能用 |

## 不要 cookbook 的话 (avoid)

❌ "Let me clarify the requirements" / "What's the QPS?"
❌ "I'm going to follow a standard recommendation pipeline..."
❌ "Which surface — mobile or web?" (broad surface clarify)
❌ Triage email / push / in-app / portal 维度

✅ "I'll assume we're optimizing for Reels home feed in-app, optimizing for session-level engagement with multi-task heads as the ML core."
"""


DEFENSE = """\
# Strong Moments — 4 个完整英文台词 verbatim (面试就这么说)

下面 4 段台词是 canonical 形态，**逐字 internalize** — 不要解释 / 改写 / 缩水。在 0-5 / 5-12 / 26-32 / 38-42 分钟段精准投放。每段都遵循 **reframe / claim → 3 concrete actions with quantification → failure modes → trade-off articulation** 的结构。

---

## ⭐ Strong Moment #1 — Multimodal Lifecycle (0-5 min, framing)

**Cue**: 紧接你的 declarative open "I'll frame this as ... with two intrinsic specialties..."。

> "**First, Reels are short-form videos**, which means content understanding cannot rely on metadata or text alone. Most Reels are UGC with minimal text, and trends are visual or audio-driven. So I'd compute multimodal embeddings — a pretrained video encoder for visual frames, an audio encoder for soundtracks, and a text encoder for any captions — fused into a single content embedding **computed once at upload time**. I'd start with pretrained backbones and fine-tune on a Reels-specific contrastive objective, where co-engaged videos are positives. The embedding gets refreshed only when we improve the encoder, **roughly quarterly**. This **decouples content understanding cost from serving cost**."

**Why this is strong**: pretrained + fine-tune + upload-time compute + quarterly refresh + cost decoupling — 每一句都是 production-aware ML decision，不是 buzzword。面试官写 feedback 时会写 "candidate showed strong ML depth on multimodal lifecycle and serving-cost trade-off"。

---

## ⭐ Strong Moment #2 — Label Schema with Ambiguous Middle (5-12 min, data section)

**Cue**: 紧接你 announce "I'll start with labels since they're the most non-trivial for Reels"。

> "**Label 1: normalized watch ratio**, defined as `watch_time / video_duration`, capped at 1.0. Critical to normalize — raw watch time would systematically over-weight long content. A 3-second video watched fully should count as much as a 60-second video watched fully.
>
> Label 2: **strong positive (binary)** — explicit engagement like, comment, share, follow, save. Sparse but high-precision.
>
> Label 3: **strong negative (binary)** — early swipe-away, defined as user swiping within the first 2-3 seconds or before 20% completion. This is the implicit hard-negative signal that's unique to Reels and crucial for breaking exposure bias in negative sampling.
>
> **Important nuance: the ambiguous middle**. A user who watches 50% then swipes is genuinely ambiguous — not a hard negative, not a strong positive. I'd treat it as **weakly positive on the watch-ratio head and exclude it entirely from the early-skip head**. Forcing a binary label on ambiguous data adds noise.
>
> One thing I want to flag: **video duration is a confounder** for almost every engagement label. A 5-second loop is much easier to complete than a 60-second clip. So duration becomes both a feature input and an evaluation slice — we should be looking at metrics conditioned on duration buckets, not just aggregate."

**Why this is strong**: 3 head + ambiguous middle 处理 + duration confounder — 是 label design 的 nuance signal。普通候选人只说 "I'll use clicks as label"。

---

## ⭐ Strong Moment #3 — Exposure Bias Reframe (26-32 min, bias section)

**Cue**: 紧接你提 IPS 作为铺垫后，"**But I want to push the framing further**..."。

> "**But I want to push the framing further** — I'd reframe exposure bias as a **system-level data acquisition problem, not just a training-time statistical correction**. Three places we can intervene:
>
> **First, onboarding as labeled exploration**. New users go through cold-start anyway. Rather than treating cold-start as a constraint to overcome, treat it as an opportunity to collect high-quality preference labels under controlled exposure — surface a curated diverse set covering distinct content clusters, and use early engagement as relatively unbiased preference signals.
>
> **Second, periodic re-exploration for existing users**. Allocate a small fraction — say 5% — of impressions per session to controlled exploration: content from under-represented clusters relative to the user's recent history. Dual purpose: bias mitigation and interest-drift detection.
>
> **Third, content-side cold-start ramp**. New uploads have no engagement history. Guarantee fresh content an impression budget in its first hours, gated by quality filters to avoid spam capture.
>
> **Failure modes to watch**: (1) exploration budget being gamed by low-quality content — mitigate with quality eligibility filters; (2) UX degradation from over-aggressive exploration — cap per-session budget and A/B test; (3) exploration data still being biased if retrieval already filtered out long-tail — need to ensure exploration draws from a wider candidate pool than production retrieval.
>
> **Why this matters more than IPS alone**: IPS corrects bias in the data you have. This approach changes the data you collect. **It's a stronger lever, but it requires cross-functional cost** — product and growth pay part of the bill that ML would otherwise pay in accuracy loss."

**Why this is strong**: reframe + 3 concrete intervention points + 量化 (5%) + failure modes + cross-functional cost articulation。面试官会写 "showed sophisticated thinking on exposure bias as data acquisition policy, not just IPS"。

**Bonus closer (objective combination)**:

> "On objectives, I'd combine three: user engagement (multi-head), ecosystem value (creator retention, content diversity at the platform level), and compliance/safety. Combination strategy: multi-task heads for engagement and ecosystem, but **compliance applied as a hard filter at re-ranking, not as a loss term**. Compliance violations aren't 'less engagement' — they're disqualifying. **Treating them as a soft loss term is a category error** that recommendation teams often make."

---

## ⭐ Strong Moment #4 — Zoom-out + Top 3 Risks (38-42 min, before serving)

**Cue**: 主动开启，"**Let me zoom out for a moment** and summarize the design, then flag the top risks I see"。

> "**Let me zoom out for a moment** and summarize the design, then flag the top risks I see.
>
> We have a **two-stage retrieval-plus-ranking system with multimodal content understanding, multi-task ranking heads, session-aware features, exposure bias mitigation via active exploration policy, and evaluation across offline, online, and long-term layers**.
>
> The top three risks:
>
> **Risk 1: Exposure bias compounding faster than mitigation can correct**. Our mitigations are partial — 5% exploration budget may not be enough if the feedback loop is strong. I'd want to **monitor content diversity served over time and have a circuit breaker if diversity drops below threshold**.
>
> **Risk 2: Multi-task loss imbalance over time**. Heads may drift in relative importance as the data distribution shifts. I'd **build retraining pipelines that re-tune head weights, not just retrain weights at fixed loss combinations**.
>
> **Risk 3: Long-term engagement versus short-term watch time**. Watch-ratio optimization can be gamed by clickbait or rage content. The pairing with explicit engagement signals partially addresses it, but **the real defense is the long-term holdout and quality-survey signals** I mentioned in evaluation. **If we ever see watch ratio going up but retention going down, that's the most important alarm**.
>
> Are there parts of the design you'd like me to deepen?"

**Why this is strong**: 3-sentence summary + 3 risk 每个包含 mechanism + mitigation + alarm signal + invite deepening — 是 E5 边界 signal，也是 E4 strong 必备。

---

## 不要这样收尾 (avoid)

❌ "I think that's all I have." (passive close — 浪费 collaborative-mode 机会)
❌ "I'm done." (no invite)
❌ "Want to discuss serving?" (低优先级 fallback — serving 主动 deprioritize 才是 strong signal)

## 应该这样收尾 (do)

✅ "Are there parts of the design you'd like me to deepen?"
✅ "I won't go deeper on serving unless you'd like — happy to discuss monitoring or rollback if useful."
"""


VERBAL_OUTLINE = """\
# Verbal Patterns + Drift Recovery 句式 + ML-native YES/NO 对照表

## 1. 开场 declarative patterns (前 90s 不澄清)

- "I'll frame this as **X** with **two intrinsic specialties** that will drive most of my design decisions..."
- "I'm choosing not to deep-dive on [X, Y] for now, but I'll flag them as risks later."
- "Does this framing make sense, or is there a different angle you'd like me to anchor on?"

## 2. Body 段 sub-structure announce

- "Let me walk through this in **N parts: A, B, C**. I'll start with [A] since [it's most non-trivial / it sets up the rest]."
- "Features fall into **four buckets**: [list 4]. The non-trivial design choice here is [pick 1]..."
- "Two-stage: **retrieval and ranking**. Retrieval: [40s]. Ranking: [40s]. Want me to deepen retrieval, ranking architecture, or the multi-task head design?"

## 3. Strong moment / reframe 句式

- "**I want to push the framing further** — I'd reframe **X as Y**, not just **Z**."
- "**Why this matters more than [standard approach]**: [trade-off articulation in 1 sentence]"
- "**Treating X as a soft Y is a category error**" (senior phrasing — 用 1 次即可，多用会显得 dogmatic)
- "**One thing I want to flag**: [a non-obvious risk / confounder]"
- "And **this is where Reels diverges** from [standard X]..."

## 4. Drift recovery / 节奏自救句式

如果发现自己飘了：

- 飘到 generic SD 词汇 → "**Let me return to the ML core** — the more important question is [X]."
- 列了太多 topic → "**Let me prioritize the top 2**: [A, B]. I'll come back to the rest if there's time."
- 退化到 one-liner mode → "**Let me go deeper on this** — there's a non-obvious nuance: [X]"
- 面试官表情困惑 → "**Let me park that, more important is** [X]."
- 列完 N bullets 没 expand → "**Pick 1**: [B]. The reason this matters is [X], and the trade-off is [Y]."

## 5. Hand-off / collaborative mode 句式

- "Let me **hold that thought** and move to **X** unless you want to deepen **Y** first."
- "Want me to **deepen retrieval, ranking, or multi-task heads**?"
- "Are there **parts of the design you'd like me to deepen**?"
- "I won't go deeper on **serving** unless you'd like — happy to discuss monitoring or rollback if useful."

## 6. Quantification 句式 (senior signal — 数字让你显得 senior)

- "**A two-tower with 128-dim embeddings** can do ~10k candidate scoring in single-digit ms on CPU, which fits our latency budget; a cross-encoder would be **100x slower** so we reserve it for top-100 reranking."
- "Three channels: **60/20/20** — personalized / trending / diversity."
- "**5% per-session impression budget** for controlled exploration."
- "**30+ day long-term holdout** for delayed effects."
- "Encoder refresh **quarterly**, single-video embedding **once at upload**."

数字不精确 OK — 方向对就行。

## 7. Production scar 句式 (E4 senior signal — 1-2 个就够)

- "**In my past work**, we found that [X happened]. So I'd [Y] before [Z]."
- "**One thing we learned the hard way**: [X]. The fix was [Y]."

## 8. ML-native YES / NO 对照表

每一句话出口前 1 秒审查 vocabulary。

### YES — 主动用 (ML SD round 必须高密度出现)

| Category   | Terms                                                                                   |
|------------|-----------------------------------------------------------------------------------------|
| Model      | model class / two-tower / DLRM / DCN / MMoE / multi-task heads / shared backbone        |
| Data       | label / impression / engagement / strong positive / hard negative / ambiguous middle    |
| Feature    | feature / embedding / cross feature / session-context / static vs dynamic / staleness   |
| Bias       | exposure bias / propensity / IPS / feedback loop / cold-start / exploration             |
| Objective  | objective / multi-task / Pareto / head weighting / engagement vs retention              |
| Evaluation | NDCG / AUC / calibration / counterfactual replay / long-term holdout / offline-online alignment |
| Production | freshness / drift / monitoring / circuit breaker / quality eligibility filter           |

### NO — 被动用 (面试官主动问 serving 才出现, 不要主动 surface)

| Category    | Terms (avoid主动)                                                          |
|-------------|----------------------------------------------------------------------------|
| SLA / NFR   | SLA / NFR / FR / availability / latency budget                             |
| Throughput  | QPS / read-write ratio / fan-out                                           |
| Infra       | service / API / cache / network / replication / partition / quorum         |
| Storage     | bandwidth / disk / IOPS / index size                                       |

**Why this matters**: Reels MLSD round 主动 surface infra 词汇 = 立刻 down-leveled。前 5 分钟独裁式 framing 一句 infra 词汇都不应该有。
"""


CHEAT_SHEET = """\
# 速查表 (Cheat Sheet) — 30s flash review before walking into Meta MLSD

## 元结构一图概览

```
Framing (60-90s)
├── 2 specialty thesis (each 45-60s)
├── what / why-Reels-specific / ML implication / cost
└── Active deprioritize + yes/no check

Body段 (每段)
├── Sub-section announcement ("N parts: A, B, C")
├── List bullets → pick 1 expand to 60s
├── Surface 1 non-obvious risk / confounder
└── Transition with "unless you want to deepen X"

Strong Moment (4 个预分配)
├── State the reframe / non-standard claim
├── 3 concrete actions with who/what/cost/量化
├── Failure modes + mitigation
└── Trade-off articulation ("why this beats X")

Zoom-out (3 min before end)
├── 3-sentence summary
├── Top 3 risks with mechanism + alarm signal
└── Invite deepening
```

## 时间锚点 (memorize)

| Time   | Stage                          | Strong Moment        |
|--------|--------------------------------|----------------------|
| 0-5    | Framing                        | **#1** Multimodal lifecycle |
| 5-12   | Data & Labels                  | **#2** Label schema + ambiguous middle |
| 12-18  | Features                       | —                    |
| 18-26  | Model (ask which side to deepen) | —                  |
| 26-32  | Bias & Objectives              | **#3** Exposure bias reframe |
| 32-38  | Evaluation                     | —                    |
| 38-42  | Zoom-out + Top Risks           | **#4** Top 3 risks   |
| 42-45  | Serving (light) + Q&A          | —                    |

## 偏好节奏 meta-rules (8 条铁律)

1. **前 90 秒不要问澄清问题** — 直接 propose framing 并用 yes/no 收尾
2. **每个开放问题给 60-90 秒回答** — 不要 30 秒，不要 2 分钟
3. **列完 N 个 bullets 立刻 pick 1 expand** — 机械规则，不要例外
4. **每个 strong moment 包含 trade-off** — "X is stronger but costs Y"
5. **每 8-10 分钟主动 zoom-out 或邀请方向选择** — 避免线性 brain dump
6. **当面试官表情困惑时立刻 park 当前 topic** — "let me park that, more important is..."
7. **Serving 段主动短** — 这是 deprioritize signal
8. **Wrap 时一定有 top-N risks** — 这是 E5 边界 signal，也是 E4 strong 必备

## 4 strong moment one-liner cue (memorize entry phrase)

| # | Entry phrase                                                                       |
|---|------------------------------------------------------------------------------------|
| 1 | "First, Reels are short-form videos..."                                            |
| 2 | "Label 1: normalized watch ratio..."                                               |
| 3 | "But I want to push the framing further..."                                        |
| 4 | "Let me zoom out for a moment and summarize the design..."                         |

## E4 not E5 — 边界提醒

✅ DO: confident execution of standard playbook + 1-2 deeper insights
✅ DO: pick a reasonable model and justify with clear trade-offs
✅ DO: identify the top 2-3 risks in the design
✅ DO: show production sense (data freshness, monitoring, rollback)
✅ DO: drive the conversation forward without getting stuck

❌ DON'T: invent novel methods
❌ DON'T: over-scope ("2 years out we'd...")
❌ DON'T: cookbook language ("I'm going to follow a standard recommendation pipeline...")
❌ DON'T: triage email/push/in-app/portal surface 维度

## 复用范围 (适用于其他 Meta 题型)

本 golden example 的结构 **80% 直接复用** 于:

- **Feed ranking** (Facebook Newsfeed / Instagram Feed) — 把 "session-based continuous consumption" 改成 "pull-based with feed position"
- **Notification ranking** — 加 send-or-not gating layer (Strong Moment #1 reframe)
- **Friend recommendation** — content embedding 换成 user-user graph embedding
- **Ads ranking** — multi-task heads 加 bid / pCVR + auction logic
- **Reels recommendation (本题)**
- **Search ranking** — query encoder 加进 retrieval tower

ML 底层框架 (2-stage funnel + multi-task + bias mitigation + offline-online-holdout 3 layer eval) **不变**，每题独立 twist 投放 strong moment #1。
"""


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _content_hash(payload: dict[str, str | None]) -> str:
    keys = (
        "title", "subtitle", "overview", "architecture", "dataflow",
        "formulas", "production_constraints", "tradeoffs", "defense",
        "verbal_outline", "cheat_sheet",
    )
    h = hashlib.sha256()
    for k in keys:
        v = payload.get(k) or ""
        h.update(k.encode("utf-8"))
        h.update(b"\x00")
        h.update(v.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def upsert(cur: sqlite3.Cursor, dry: bool) -> str:
    now = _now()
    payload: dict[str, str | int | None] = {
        "slug": SLUG,
        "title": TITLE,
        "subtitle": SUBTITLE,
        "diagram_filename": None,
        "overview": OVERVIEW,
        "architecture": ARCHITECTURE,
        "dataflow": DATAFLOW,
        "formulas": FORMULAS,
        "production_constraints": PRODUCTION_CONSTRAINTS,
        "tradeoffs": TRADEOFFS,
        "defense": DEFENSE,
        "verbal_outline": VERBAL_OUTLINE,
        "cheat_sheet": CHEAT_SHEET,
        "display_order": DISPLAY_ORDER,
        "source_path": SOURCE_PATH,
        "updated_at": now,
    }
    payload["content_hash"] = _content_hash(
        {k: (v if isinstance(v, str) else None) for k, v in payload.items()}
    )

    cur.execute("SELECT id FROM system_designs WHERE slug = ?", (SLUG,))
    row = cur.fetchone()
    if row:
        if dry:
            return f"DRY UPDATE id={row[0]} slug={SLUG}"
        cols = ", ".join(f"{k} = :{k}" for k in payload)
        cur.execute(
            f"UPDATE system_designs SET {cols} WHERE slug = :slug", payload
        )
        return f"updated id={row[0]} slug={SLUG}"

    payload["created_at"] = now
    cols = ", ".join(payload.keys())
    placeholders = ", ".join(f":{k}" for k in payload)
    if dry:
        return f"DRY INSERT slug={SLUG} display_order={DISPLAY_ORDER}"
    cur.execute(
        f"INSERT INTO system_designs ({cols}) VALUES ({placeholders})", payload
    )
    return f"inserted id={cur.lastrowid} slug={SLUG} display_order={DISPLAY_ORDER}"


def validate(cur: sqlite3.Cursor) -> list[str]:
    """Run the 7 validation checks from the task spec."""
    errs: list[str] = []

    cur.execute(
        "SELECT id, slug, title, subtitle, display_order, overview, architecture, "
        "dataflow, formulas, production_constraints, tradeoffs, defense, "
        "verbal_outline, cheat_sheet, content_hash, updated_at "
        "FROM system_designs WHERE slug = ?",
        (SLUG,),
    )
    rows = cur.fetchall()
    if len(rows) != 1:
        errs.append(f"AC1 FAIL: expected exactly 1 row for slug={SLUG}, got {len(rows)}")
        return errs

    row = rows[0]
    (rid, slug, title, subtitle, disp_order, overview, architecture, dataflow,
     formulas, prod_cons, tradeoffs, defense, verbal, cheat, chash, upd_at) = row

    prose_cols = {
        "overview": overview,
        "architecture": architecture,
        "dataflow": dataflow,
        "formulas": formulas,
        "production_constraints": prod_cons,
        "tradeoffs": tradeoffs,
        "defense": defense,
        "verbal_outline": verbal,
        "cheat_sheet": cheat,
    }
    for k, v in prose_cols.items():
        if v is None:
            errs.append(f"AC2 FAIL: column {k} is NULL")
        elif len(v) <= 200:
            errs.append(f"AC2 FAIL: column {k} length={len(v)} <= 200")

    total_bytes = sum(len((v or "").encode("utf-8")) for v in prose_cols.values())
    if total_bytes <= 8000:
        errs.append(f"AC3 FAIL: total prose bytes={total_bytes} <= 8000")

    expected_phrases = [
        "First, Reels are short-form",
        "Label 1: normalized watch ratio",
        "But I want to push the framing further",
        "Let me zoom out for a moment",
    ]
    for phrase in expected_phrases:
        if phrase not in (defense or ""):
            errs.append(f"AC4 FAIL: phrase {phrase!r} not in defense column")

    if "Meta MLSD Golden Example" not in (subtitle or ""):
        errs.append(f"AC5 FAIL: subtitle missing 'Meta MLSD Golden Example' substring")

    if not chash:
        errs.append("AC6 FAIL: content_hash is empty")
    if not upd_at:
        errs.append("AC6 FAIL: updated_at is empty")

    cur.execute(
        "SELECT COUNT(*) FROM system_designs WHERE display_order = ?",
        (DISPLAY_ORDER,),
    )
    cnt = cur.fetchone()[0]
    if cnt != 1:
        errs.append(
            f"AC7 FAIL: display_order={DISPLAY_ORDER} has {cnt} rows (expected 1)"
        )

    print(f"[OK] row id={rid} slug={slug}")
    print(f"     title={title[:60]}...")
    print(f"     display_order={disp_order}, total prose bytes={total_bytes}")
    for k, v in prose_cols.items():
        print(f"     {k}: {len(v or '')} chars")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"ERROR: db not found: {db_path}", file=sys.stderr)
        return 1

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    action = upsert(cur, args.dry_run)
    print(action)

    if args.dry_run:
        con.rollback()
        print("\nDRY-RUN: rolled back")
        con.close()
        return 0

    con.commit()
    errs = validate(cur)
    con.close()

    if errs:
        print("\n[FAIL] validation errors:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("\n[DONE] all 7 ACs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
