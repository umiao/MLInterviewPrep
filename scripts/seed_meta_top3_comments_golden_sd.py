"""Seed: T-P0-853 [Meta-MLSD] Top-3 Comments Golden -> system_designs.

INSERTs (or idempotently updates) the canonical Meta MLSD Top-3 Comments
golden example as ``system_designs(slug='meta-top3-comments-golden')``,
drawer-reachable via ``sd://meta-top3-comments-golden``. Sourced verbatim from
``docs/prep/meta_mlsd_2026-05-12_top3/source_04_top3_comments_golden.md``
(user-authored Discord msg 1503871555216605214 Part 4 Golden Answer + Part 5
Mock Checklist + msg 1503874418802163744 Bias Tower / Shadow Logging reference).

Mirrors the structural shape of `scripts/seed_meta_reels_golden_sd.py` (sd41):
9 prose columns all non-NULL, each > 200 chars, total content > 8000 bytes,
sentinel-based UPSERT by slug, dry-run flag.

Architecture and production_constraints both embed a short Bias Tower /
Shadow-Logging digest with an anchor sentence pointing to fr-node
``meta-prep/system-design-must-knows/popularity-bias-debiasing`` (id=266)
for the 深版 walkthrough (T-P0-854 owns that 深版).

Cheat_sheet ends with the user's 4 Design Doc 强调话术 sentences verbatim.

Usage::

    python scripts/seed_meta_top3_comments_golden_sd.py [--db data/mle_prep.db] [--dry-run]
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

SLUG = "meta-top3-comments-golden"
TITLE = "Meta MLSD Golden Example: Top-3 Comments under a Post (45min walkthrough)"
SUBTITLE = (
    "Meta MLSD Golden Example -- canonical 3-twist framing (comment != item / time-bias / "
    "community-health-as-guardrail) + viewer-primary set-selection top-3 ranking. "
    "Adjacent to sd://meta-reels-golden (T-P0-837); cross-link via cd://94 Q1 + cd://95/96/97 drawers."
)
DISPLAY_ORDER = 131
SOURCE_PATH = "docs/prep/meta_mlsd_2026-05-12_top3/source_04_top3_comments_golden.md"

ANCHOR_FR_NODE = "meta-prep/system-design-must-knows/popularity-bias-debiasing"


OVERVIEW = """\
# Top-3 Comments under a Post -- 45min Golden Walkthrough

## 整体节奏哲学 (Opening 60s + 时间分配 + 3 unique twists 框架)

**Opening 60s 锁三件事** (declarative, 不问 clarifying):

> "Scope: 设计一个系统，从一个 post 下的所有 comments 中选出 3 条 surface 给 viewer，
> optimize for viewer's joint experience (engagement + community health)。Retrieval 被
> 单个 post 的 comment pool 天然 bound，所以这是个 **ranking + set-selection 问题，不是
> multi-stage retrieval**。"

**3 unique twists vs generic ranking** (每个带 design implication，是后续每一段的 hook):

| # | Twist                              | Design implication                                              |
|---|------------------------------------|-----------------------------------------------------------------|
| 1 | **Comment != item**                | 超短文本 + 作者是 user graph 节点 + social signal 是主信号；text + social fused representation，commenter 当 sub-entity |
| 2 | **Time-bias**                      | 早发的 comment 抢曝光；engagement velocity (rate not count) 当 feature，bandit explore 补晚评论 |
| 3 | **Adversarial + community health** | 进 **guardrail**，不进主优化目标；独立 abuse model + toxicity hard filter pre-ranker |

**Time plan (declarative, 不让面试官分配)**:

- **15 min 前段**: framing / metric / label / feature
- **25 min 后段**: model + serving + monitoring
- 收尾 yes/no: 等点头就推进

## 与 sd41 (Reels Golden) 的关键差异

| Dim                | sd41 Reels                            | sd131 Top-3 Comments (本题)                         |
|--------------------|---------------------------------------|-----------------------------------------------------|
| Retrieval          | 2-stage funnel, multi-channel 60/20/20| **Trivial bounded by post's comment pool, 不展开**  |
| Output             | Ordered feed (linear consumption)     | **Top-3 set selection (list-level)**                |
| ML formulation     | Point-wise ranking + multi-task heads | Point-wise ranking + **MMR reranker with hard quota** |
| Negative label 难点 | Early-skip implicit signal            | **Selection bias on unexposed comments** (IPS + bandit) |
| Metric             | Session-level engagement              | **List-level diversity + any-engagement rate**      |
| Community health   | Hard filter (compliance)              | **独立 abuse model + tiered action (filter / demote)** |

**Why this matters**: top-K / carousel / multi-slot 题目 (top-3 comments / top-K
search results / multi-slot ads) 与 ordered feed 题目 (Reels / Newsfeed) 在 **metric
+ architecture (ranker vs reranker)** 段必须显式区分。开场就说 "this is a set-selection
problem, not pure ranking" 是 E5 边界 signal。

## E4 not E5 -- 边界提醒

不要 invent novel methods (e.g. learned DPP kernel for n=3 list)，不要 over-scope
("2 years out we'd train a custom comment-LLM..."). 要的是 **confident execution of
standard playbook + 1-2 deeper insights** (本题 deeper insights = Section 1 time-bias
reframe + Section 3 selection-bias 三阶 negative label)。每个决策点说出 "我选 A 因为 X，
代价是 Y，如果 Z 变化我会切到 B" -- 见 tradeoffs col 8 个 trade-off matrix。
"""


ARCHITECTURE = """\
# Architecture: 2-stage Pointwise Ranking + MMR Set-Selection Reranker

## Section 5.1 Architecture verbatim (本题核心 6 min)

Funnel (top-down, 每层 budget 明确):

```
Pre-filter (toxicity hard filter + dedup, in-storage)  -> 1000 candidates
L1 pre-rank (GBDT, cheap features, weighted target)    -> top 100-200
L2 deep rank (MMOE + shallow bias tower)               -> point-wise scores
Reranker (MMR with hard quota)                         -> top 3
```

**L2 ranker 详细架构 (这是核心 -- 必须 expand 90s)**:

```
+--------------------------------------------+
| Main tower (Deep + Cross)                  |
|  +- Head 1: engagement                     |
|  +- Head 2: toxicity (also pre-filter)     |
|  +- Head 3: diversity-contrib              |
+--------------------------------------------+
| Shallow bias tower                         |
|  Input: position / popularity / recency    |
|  Output: additive at training              |
|           MASKED at inference  <- 关键     |
+--------------------------------------------+
```

**Multi-task 起点**: shared bottom + 多 head + 合成 label，**升级到 MMOE 只有在 negative
transfer 出现时** -- 不要一上来就 MMOE。Loss weight 由 biz context 锁 (comment 相对 like
的 lift 价值 + risk budget)，**不是 uncertainty weighting** -- 因为 weight 本质是产品
决策，不是统计估计。

**Reranker 选择 MMR 不 DPP** (本题最重要的 architectural trade-off):

- **Why MMR**: n=3, list 太短，DPP 的 set-level optimization 没空间体现 -- 3 个 item
  的 determinant 几乎被任意一对 cosine 主导
- **Method**: MMR across 3 axes (commenter / sentiment / topic) + **hard quota**
  (no 2 same commenter, <=1 OP self-reply)
- **Future upgrade signal**: DPP with learned kernel **when list 扩到 top-10+** --
  这是 senior 写 trade-off 的方式: 不说 "MMR is better"，说 "MMR for this regime, DPP
  if regime changes"

==> 下段缝合: **3 head 对应 Section 2 的 3 proxy；shallow tower 实现 Section 3 承诺的 debias**。

## Bias Tower 简版 (本段末尾自含 -- 深版见 fr-node)

**3 句核心 (verbatim from 用户参考资料第 一/二/三 节)**:

1. **加性结构 + 容量瓶颈**: `logit = main_tower(content, user, ctx) + bias_tower(bias_features)`，
   主塔深 (MMoE)，偏差塔浅 (1-2 层 / 线性)。偏差塔输入**只放 bias 类特征** (position /
   device / slot type / isAds)。浅的 inductive bias = **吃不下 content 信号**，只能
   吸收加性偏置 -> 主塔被逼学真实相关性。
2. **Mask-at-inference**: 训练时 bias tower 喂真实 position；推理时 **bias term 整个
   置 0** (或 position 设固定参考值)。配套训练技巧: position feature dropout 让模型对
   缺失鲁棒。
3. **Bias tower vs 直接当 feature**: bias tower **加性可分**，推理 mask 良定义；拼进
   主塔 -> content x position 纠缠，推理时分布外、表示被污染、position 抢梯度。理论
   等价的前提 (position 随机分布 + dropout + 正则 + 大容量) = 手工搭 bias tower。

**深入见 fr-node `""" + ANCHOR_FR_NODE + """`** -- 涵盖 isAds counterfactual
vs context-feature 判断标准、shadow logging 与 bias tower 的耦合、口诀 (架构纠偏 +
推理纠偏 + 数据纠偏，三层缺一不可) 等深版内容 (T-P0-854 owns)。

## Architectural choices 对应回 framing 的 3 twists

| Twist                       | Architectural choice                                                       |
|-----------------------------|----------------------------------------------------------------------------|
| Comment != item             | Comment text embedding @ creation + commenter sub-entity features in main tower |
| Time-bias                   | Engagement velocity feature (rate, not count) + shallow bias tower mask    |
| Adversarial / community     | Toxicity hard filter pre-ranker + **independent abuse model** (no share weights) |
"""


DATAFLOW = """\
# Dataflow: Section 1-4 Verbatim (前段 14 min framing + metric + label + feature)

## Section 1: Framing (4 min)

"L1 (user): **Viewer 是主用户** -- 他们消费 comments 决定是否参与。Commenter 和 OP 是
secondary stakeholder，进 joint experience guardrail。

L2 (scale): **100M DAU, ~10% commenting rate, viral post peak 100x average, p99 < 200ms**。

L3 (twists with implications):

- **Comment != item** -> 需要 text + social fused representation，commenter 当 sub-entity
- **Time-bias** -> engagement velocity (rate not count) 当 feature，bandit explore 补晚评论
- **Community health** -> 独立 abuse model + toxicity hard filter pre-ranker

L4 (ML formulation): **2-stage point-wise ranking** (cheap pre-rank -> deep rank) +
**list-level reranking** (MMR for diversity)。Retrieval trivial 不展开。

==> 下段缝合: 这 3 个 twist 每个都会 hook 到下一段的具体 metric 或 guardrail。"

## Section 2: Metrics (3 min)

"**L1 North-star**: **weekly commenter return rate** -- 一个数，不并列。捕捉
「看到好的 top-3 -> 愿意参与 -> 长期回流」。

**L2 Proxies (3, 每个一句 alignment)**:

- Comment-area dwell time -> top-3 有趣 -> 用户读得久 -> return ↑
- Reply rate triggered by top-3 -> top-3 引发对话 -> commenter return ↑
- Self-comment rate after top-3 -> top-3 激发参与 -> 新 commenter return ↑

**List-level metric (top-3 是 set selection)**:

- Top-3 **diversity score** (sentiment / commenter / topic 3 轴)
- Set-level user satisfaction (post-view next-action distribution)

**L3 Guardrails (指标 + 阈值 + enforce 机制)**:

- Toxicity rate < 0.5% -> hard filter pre-ranker
- Report rate per 1k impressions < X -> A/B halt criterion
- p99 latency < 200ms -> serving constraint
- Early-post exposure share -> fairness re-weight in loss
- Group exposure gini -> fairness audit

**L4 Causal chain**: reply rate ↑ -> 用户感受到 comment area 有对话价值 -> 用户回流参与
-> weekly commenter return ↑

==> 下段缝合: north-star 和 3 个 proxy 直接定义了 label 结构 -- 下面 label 段会逐一落地。"

## Section 3: Labels (4 min) -- 本题核心难点 selection bias

"**Positive label 阶梯**:

- L1 baseline (the dumbest version): binary engagement (like / reply within window)
- L2: weighted multi-signal (reply > like > view-completion)
- **L3 (我选这层)**: engagement-to-impression ratio in rolling [T, T+1h] window
  - Trade-off: 比 raw count 复杂，但 **partial-debias 了 position bias**
- L4 (留 follow-up): multi-task labels with weighted heads

**Negative label (本题核心难点 -- selection bias)**:

- **Explicit**: dislike / report (strong signal, 直接用)
- **Exposed-not-engaged**: 标准 negative
- **Unexposed**: treat as **unknown** + IPS-weighted + bandit-exploration backfill
  - Why not 'unexposed = negative': 引入巨量 false negative (好 comment 只是没曝光过)
  - Trade-off: 工程复杂，但理论正确

**Imbalance ladder (stop at L2, 留 L3/L4 给 follow-up)**:

- L1: stratified sampling
- L2: class-weighted loss

**Bias handling**: popularity / position / freshness -> **shallow bias tower，serving
时 mask 输出** (YouTube 2019 做法，比 mask input feature 更稳，因为 model 不能从其他
feature 重建 bias)。

**Leakage guard**: feature snapshot @ T, label observation @ [T, T+ΔT], **no overlap**。

==> 下段缝合: multi-task label (engagement / quality / safety) 定义了下面 architecture
需要的 head 数量。"

## Section 4: Features (3 min) -- 4 象限模型

"**4 象限模型，每象限 3 个 + 1 个 comment 独有**:

**User (viewer)**:

- Demographic + topic preference embedding
- Viewer 历史 comment engagement rate
- Viewer sentiment preference (likes positive / debate / sarcasm)

**Item (comment + commenter sub-entity)** -- 这象限含本题独有项:

- Comment text embedding (computed once at creation)
- **Early engagement velocity** (rate-based, time-debiased) <- 对应 Section 1 time-bias twist
- **Commenter identity** (verified / OP / followed-by-viewer) <- 对应 comment != item twist
- Toxicity / sentiment score (bonus, 喂 quality head)

**Context**:

- Post topic + age
- Time of day + day of week
- Device + session intent

**Interaction (viewer x this specific comment)** -- ranking 比 single-tower retrieval
强大的根源:

- Viewer x commenter follow relationship
- Semantic similarity (viewer's comment history vs this comment)
- Viewer's historical engagement with this commenter

**Critical distinction**: Interaction features 是 per-(user, item) pair, serving 时
**每条 candidate 算一次**。这是 ranking 比 single-tower retrieval 强大的根源 --
two-tower 永远算不出 user x item interaction，只能 dot product。

==> 下段缝合: comment embedding 喂 L2 ranker 主路；interaction features 在 DCN 风格
cross layer 里和 user embedding 交叉。"
"""


FORMULAS = """\
# Label Ladder + Negative Sampling Ratio + Train/Eval Split 双轴 + Multi-task Conflict

## Positive label 阶梯 (L1 -> L4, 我选 L3)

| Level | Label                                                              | Trade-off / Why                                  |
|-------|--------------------------------------------------------------------|--------------------------------------------------|
| L1 (dumbest) | binary engagement (like / reply within window)              | sparse + position-biased                         |
| L2     | weighted multi-signal (reply > like > view-completion)             | 工程不难，但仍有 position bias                   |
| **L3 (pick)** | **engagement-to-impression ratio in rolling [T, T+1h] window** | partial-debias position bias, time-aware         |
| L4 (follow-up) | multi-task labels with weighted heads                          | 留 senior follow-up，主题是 head weighting design |

**Pick justification**: L3 比 L2 多一步 **rolling-window normalize by impression count**，
这一步直接除掉了 position 高的 comment 自带的 impression 优势 -- 是 partial debias
**前置到 label 层**，比单纯靠 model-level bias tower 多一道防线。

## Negative sampling batch composition (具体比例)

```
1   positive (exposed + engaged)
: 3-5 exposed-not-engaged (IPS-weighted)
: 1-2 unexposed (from bandit exploration data)
: 0.5-1 hard negative (mined from 上一轮 model 高分但未 engage)
```

**Three 关键 design decisions**:

1. **IPS-weighted exposed-not-engaged**: propensity = P(item exposed | user, context)
   from a separate logging-policy model；low-propensity item 的 not-engaged sample
   weight 较高 (counterfactual correction)
2. **Bandit exploration backfill for unexposed**: 5% per-session impression budget
   for controlled exploration -> 这些 imps 进 train set 提供 unbiased label on
   under-exposed long tail
3. **Hard negative mining from previous model**: 高 prediction 但 not engaged 的
   item -> 教 model 区分 confidence-high mistakes

**Why not 'unexposed = negative'** (initial intuition 错的): 引入巨量 false negative
-- 一个好 comment 可能只是 retrieval 没碰到，强行打 0 label 教 model "好东西也不好"，
是 selection bias 的最差 manifestation。

## Train/eval split (双轴)

**主轴 -- time-based**:

- Train: `[T - 30 days, T - 1 day]`
- Eval: `[T - 1 day, T]`
- **Why time-based not random**: comment ranking 是 **freshness-sensitive task**，
  random split leak future popularity trend (a viral comment 在 train period 已经
  spike，eval split 里它的 future popularity 已被 train 看到 -> AUC 虚高)

**次轴 -- user-level holdout**:

- 每个时间窗 **5% user holdout**, 测 user generalization
- 这一轴 catches "model memorize specific users instead of learning preferences"

**Feature snapshot**: 对齐 train/eval 时间，**daily snapshot strategy** -- 每天定时把
所有 feature value 落盘，train 用对应 day 的 snapshot，**point-in-time correct，no
future leakage**。

## Multi-task conflict (engagement vs toxicity) -- 三选项对比

| Option                                       | Mechanism                                                                  | Why pick / not pick                                              |
|----------------------------------------------|----------------------------------------------------------------------------|------------------------------------------------------------------|
| **Pick: Hard constraint via pre-filter + soft penalty in engagement head** | Toxicity > threshold -> pre-filter 移除；剩余 candidates 主 head 用 BCE + 弱 toxicity penalty term | Audit 容易、failure mode 清晰、E4 边界标准答案 |
| Gradient surgery (PCGrad / GradVac)          | Project conflicting gradients orthogonal to each other                     | **复杂度不值得** -- top-3 ranking 不是 GradNorm-class 高竞争 multi-task |
| Reward shaping into single label             | `score = engagement - lambda * toxicity` 合成 label                        | **保 eval diagnostic 能力** -- 单一 label train 后无法分离归因，monitor head 也丢了 |

**Pick justification**: pre-filter (hard constraint) 处理 disqualifying violation +
soft penalty (engagement head) 处理 borderline case + monitor head (不参与 loss) 提供
diagnostic -- 三层职责清晰且 audit-able。E4 face level 不需要 PCGrad。

## Score combination (post-train tunable)

```
final_score = w_1 * p_engagement + w_2 * p_diversity_contrib + (- w_3 * p_toxicity)
```

权重 `w_k` **post-train tunable** -- 无需 retrain 即可 ship engagement-vs-quality
trade-off A/B。`p_toxicity` 项参考 Reels golden 同样用 `(1 - p)` 形式 (高 score = unlikely toxic)
也可以 -- 数学等价。
"""


PRODUCTION_CONSTRAINTS = """\
# Production Constraints (Section 5.3 Serving Verbatim + Shadow-Logging 简版)

## Section 5.3 Serving (6 min, verbatim)

**Latency budget (p99 < 200ms, 五层 breakdown)**:

| Stage                                            | Budget   |
|--------------------------------------------------|----------|
| Candidate retrieve + parallel feature prefetch   | **60 ms** |
| Storage-local pre-filter                         | **10 ms** |
| L2 ranker (DNN batch 100-200)                    | **80 ms** |
| Rerank feature fetch + MMR                       | **30 ms** |
| Aggregation + serialize                          | **20 ms** |
| **Total**                                        | **200 ms** |

**关键设计**:

- **Feature prefetch 在 candidate retrieve 阶段就并行发 RPC** -- 到 ranker 时
  feature 已在内存。这是 60ms 这层就跑 prefetch 的原因，不等 pre-filter 完。
- Reranker 只要 30ms 因为 n=3 时 MMR 几乎免费，主要开销是 sentiment / commenter group
  的额外 feature fetch。

## Tiered refresh strategy (5 档, 不是一刀切)

| Cadence              | What                                                                       |
|----------------------|----------------------------------------------------------------------------|
| **Streaming 1-5 min**| engagement velocity, recent counts, real-time toxicity flag                |
| Hourly batch         | aggregated like rate, cumulative stats                                     |
| Daily batch          | user profile, commenter reputation, topic preference                       |
| At creation          | comment text embedding (compute once, never recompute)                     |
| Daily / Quarterly    | ranker model retrain (daily) / embedding model contrastive retrain (quarterly) |

**关键**: **engagement velocity 必须 streaming** -- 否则 Section 1 承诺的 time-bias
mitigation 跑不起来。这是 Section 1 framing 的产品承诺 -> serving 段的 streaming
infra cost 之间的 **explicit accountability chain**。

## Serving-skew prevention (工业标准 2 件套) + Cache

**2-piece skew defense**:

1. **Shadow feature logging**: serving 时把实际喂给 model 的 feature 值落盘，offline
   训练用这份 log，**不再重算** -> 唯一彻底防 skew 的方法
2. **Online-offline feature parity test**: 同一个 (user, item) 在 online 和 offline
   pipeline 各算一遍，diff > 阈值告警 -- 这是 shadow logging 的 audit gate

**Cache**: hot post results 在 session 开始 cache，**5-min TTL + 新高互动 comment
触发 invalidation**。viral post 100x peak 情况下 cache 是 latency 命脉。

## Shadow Logging + Train-Serve Skew 简版 (本段末尾自含 -- 深版见 fr-node)

**4 来源浓缩 (verbatim from 用户参考资料第五节)**:

1. 训练/服务代码路径不一致 (Python vs C++)
2. Time travel: 训练特征泄漏未来
3. 数据源 / 默认值 / null 处理漂移
4. **Bias 特征训练用真实值、serving 用 mask，分布不匹配** -- 与 architecture 段 bias
   tower 直接耦合

**Shadow logging 2 件套核心句 (verbatim from 用户参考资料第六节)**:

- 保证训练/服务特征 **100% 一致** (同一份代码算的)
- **Point-in-time 正确，无未来泄漏**；bias 特征 (position / device) 忠实记录，bias
  tower 训练分布对齐 -- 否则 architecture 段的 mask-at-inference 直接被 skew 破坏

**深入见 fr-node `""" + ANCHOR_FR_NODE + """`** -- 涵盖 shadow logging 工程要点
(异步队列 Kafka/Pub-Sub 不阻塞 serving / 流式 label joiner Flink/Beam 按 request_id
关联行为 / 持续监控 logged 特征分布 vs serving 实时分布告警) 等深版内容 (T-P0-854 owns)。

## Production scar 句式 (E4 senior signal -- 1-2 个就够)

- "**In my past work**, 我们发现 shadow logging 加上线时如果不做异步队列直接 inline 写盘，
  serving p99 会跳 30%。fix 是 fire-and-forget pub-sub。"
- "**One thing we learned the hard way**: bias tower 推理 mask 那一步 forgot to dropout
  position feature in training -> 部署后 model 对 position=missing 完全炸，因为分布外。"

## 不要主动展开的 infra 词汇

QPS / SLA / availability / replication / sharding / fan-out / cache TTL / network
bandwidth -- 这些是 infra round 词汇，**ML SD round 主动 surface 就被 down-leveled**。
本题已经显式给了 latency budget (200ms) 和 viral peak (100x)，这是足够的产品语境，
**不要再去 fishing 更多 NFR**。被问到再用。
"""


TRADEOFFS = """\
# Tradeoffs (8 个决策点, 每个 "I pick A because X, costs Y, switches to B if Z")

## 1. Multi-task conflict: hard pre-filter + soft penalty  vs  PCGrad / reward shaping

**Pick**: hard constraint via pre-filter + soft penalty in engagement head。

| Option                                            | Pros                                    | Cons                                                |
|---------------------------------------------------|-----------------------------------------|-----------------------------------------------------|
| **Pre-filter + soft penalty (pick)**              | Audit 容易；failure mode 清晰；E4 标准答案 | Pre-filter threshold 是 product decision，不是 statistical |
| PCGrad / GradVac                                  | 自动 conflict 处理                      | 复杂度不值得；top-3 ranking 不是 high-competitive multi-task |
| Reward shaping into single label                  | 实现简单                                | 保 eval diagnostic 能力为 0，monitor head 也丢了    |

**Why pick**: "Top-3 ranking 不是 GradNorm-class 高竞争 multi-task，gradient surgery
是 over-engineering。Pre-filter + soft penalty 三层职责清晰且 audit-able。"

## 2. Reranker: MMR  vs  DPP

**Pick (本题最重要的 architectural trade-off)**: MMR with hard quota across 3 axes。

| Dim                | MMR (pick)                                            | DPP                                            |
|--------------------|-------------------------------------------------------|------------------------------------------------|
| List size fit      | **n=3 perfect** -- 短 list MMR 足够                   | n>=10 才能 show kernel power                  |
| Implementation     | greedy, deterministic                                 | determinant compute，learned kernel optional   |
| Tunability         | lambda 参数 + 3 axes (commenter / sentiment / topic)  | learned kernel 难审计                          |
| Future upgrade     | -> DPP **when list 扩到 top-10+**                     | -                                              |

**Why pick**: "For n=3, MMR with hard quota (no 2 same commenter, <=1 OP self-reply)
gives me deterministic diversity guarantee with auditable knobs. DPP for n=3 is
solving for n=20 with n=3 evidence."

## 3. Negative sampling: 'unexposed = negative'  vs  IPS + bandit backfill

**Pick (本题核心难点 selection bias 的 ML 解法)**: IPS-weighted exposed-not-engaged +
unexposed treated as unknown + 5% bandit exploration backfill。

| Approach                          | Why                                                              |
|-----------------------------------|------------------------------------------------------------------|
| **IPS + bandit (pick)**           | 理论正确；catches under-exposed long tail; 5% bandit explicit budget |
| Unexposed = negative              | **引入巨量 false negative**；selection bias 最差 manifestation     |
| Pure random exploration           | UX degradation 太大                                              |
| **Switching trigger**             | "If 5% bandit budget gives 0 net new positives after 4 weeks -> 拓到 8%; if commenter complaints rise -> 降到 3% with quality eligibility filter" |

## 4. Label level: L3 engagement-to-impression ratio  vs  L1 binary  vs  L4 multi-task

**Pick**: L3 (rolling-window ratio in [T, T+1h])。

**Why pick**: "L3 比 L2 多一步 normalize by impression count -- 这一步直接除掉 position
高的 comment 自带的 impression 优势，是 partial debias **前置到 label 层**，比单纯靠
model-level bias tower 多一道防线。L4 multi-task 留给 senior follow-up。"

## 5. Bias handling: shallow bias tower + mask  vs  feature input  vs  IPS only

**Pick**: shallow bias tower with mask-at-inference (YouTube 2019)。

| Dim              | Bias Tower (pick)              | 拼进主塔 feature             | IPS only                       |
|------------------|--------------------------------|------------------------------|--------------------------------|
| 分解结构         | 加性可分                       | content x position 纠缠      | training-time correction only  |
| 推理 mask        | 良定义                         | 分布外、表示被污染           | N/A (no mask)                  |
| 梯度竞争         | 主塔学相关性                   | position 抢信号              | N/A                            |
| **Why pick**: "**Bias tower + mask 是 architectural mechanism；IPS 是 statistical correction。两者不冲突 -- 但 bias tower 是 first-line 防线，IPS 是 second-line。**" |

## 6. Train/eval split: time-based + user holdout  vs  random

**Pick**: time-based 主轴 + user-level holdout 次轴。

**Why pick**: "Comment ranking 是 freshness-sensitive task -- random split leak
future popularity trend，AUC 虚高。Time-based 主轴是 must，user holdout 次轴 catches
'model memorize specific users instead of learning preferences'。"

## 7. Abuse model: independent  vs  shared weights with ranker

**Pick**: 独立 abuse model (NSFW + relevance + high-risk)，**不和 ranker share weights**。

| Dim              | Independent (pick)                                    | Shared weights                          |
|------------------|-------------------------------------------------------|------------------------------------------|
| Risk             | Ranker 无法 学 abuse pattern 形成 collusion           | Ranker 可能 internalize abuse signal as engagement proxy |
| Update cadence   | Abuse model **weekly retrain** (adversarial drift)    | Coupled to ranker retrain cycle (daily) |
| Audit            | 独立 precision/recall daily 监控                      | 混在 multi-task metric 里               |
| **Why pick**: "Adversarial drift 速度 != ranker drift 速度，独立 model + 独立 retrain schedule 是必须。" |

## 8. Loss weighting strategy: biz-context locked  vs  uncertainty weighting

**Pick**: biz context locked (comment lift 价值 + risk budget)，**not uncertainty weighting**。

**Why pick**: "**Loss weight 本质是产品决策，不是统计估计**。uncertainty weighting 是
solving statistical mismatch；biz-context lock 是 reflecting product priority。E5 边界
signal = 知道何时 ML 决策应该 defer to product。"

## 不要 cookbook 的话 (avoid)

- "Let me clarify the requirements" / "What's the QPS?" (前 60s 不澄清)
- "I'm going to follow a standard recommendation pipeline..." (cookbook)
- "Which surface -- mobile or web?" (broad surface clarify)
- "Should we use MMOE or just multi-head?" (在 architecture 段直接 announce，不要问)

## 应该这样开题 (do)

- "Scope: 设计一个系统，从一个 post 下的所有 comments 中选出 3 条 surface 给 viewer，
  optimize for viewer's joint experience..."
- "3 个 unique twists vs generic ranking: comment != item, time-bias, community-health-as-guardrail..."
- "Time plan: 15 min framing/metric/label/feature，25 min model+serving+monitoring..."
"""


DEFENSE = """\
# Section 5.4 Monitoring + A/B Verbatim (4 monitoring signals + list-level A/B + abuse model + loop closure)

## Model health monitoring (4 个 signal, ordered by leading-vs-lagging)

| # | Signal                              | Mechanism                                                                          | Leading vs Lagging  |
|---|-------------------------------------|------------------------------------------------------------------------------------|---------------------|
| 1 | **Online-offline metric gap**       | eval AUC vs online CTR divergence > X% -> alert (label leak / distribution shift 早期信号) | leading             |
| 2 | **Prediction distribution shift**   | KL divergence of model output day-over-day -> 比 metric 退化更早的 leading indicator | leading (earliest)  |
| 3 | **Feature drift**                   | PSI on top features, hourly                                                       | leading             |
| 4 | **Engagement metric**               | 24h moving avg vs baseline                                                        | lagging             |

**Why 4 信号 not 1**: 单一 engagement metric 是 lagging indicator -- 等它跌的时候用户
已经流失。Prediction distribution shift (signal #2) 是 **比 metric 退化更早的 leading
indicator** -- 这是 E4 senior signal，普通候选只说 "monitor AUC"。

## A/B 设计 for top-3 list-level (本题特殊)

**Randomization**: user-level (同 user sessions 必须 consistent -- 否则 weekly return
metric 测不准)。

**Metrics 三层**:

- **Primary list-level**: **any-engagement rate in top-3** (不是单条 NDCG/MRR) -- 本题
  特殊点: top-K / carousel / multi-slot 题目必须用 list-level metric
- **Secondary**: dwell time / reply rate / self-comment rate
- **Guardrails**: report rate / toxicity exposure / group fairness

**Ramp 策略**: 1% -> 5% -> 20% -> 50%, **automatic halt 当任一 guardrail 越界** --
不是 manual review，是 automated circuit breaker。

**North-star (weekly return) measurement**: **4-week long-horizon holdout group**,
A/B ramp 决策接受 proxy-based -- 这是 trade-off: 等不起 4 周再 launch，但保留 holdout
做 retrospective long-term validation。

## Abuse / gaming detection (独立模型 + tiered action)

**Independence rationale**: 独立模型 (NSFW + relevance + high-risk)，**不和 ranker
share weights** -- 避免 ranker 学 abuse pattern 形成 collusion。如果 abuse pattern
是 engagement proxy (e.g. shock content), shared model 会把它当 positive signal 投放。

**Tiered action** (分级响应避免 false-positive 一棒子打死):

| Confidence | Action                                              |
|------------|-----------------------------------------------------|
| Confident  | **Hard filter** (移出 candidate set, 进 pre-ranker 输入)  |
| Uncertain  | **Hard demote** (保留在 pool 但不进 top-K)         |

**Adversarial drift defense**: abuse model **precision/recall daily 监控**, **weekly
retrain**。Adversarial drift 速度 != ranker drift 速度 -- abusers actively probe
defense weekly，weekly retrain cadence 是必须。

## Loop closure (闭环 -- E5 边界 signal)

Monitoring outputs feed back into 2 places:

1. **Training data quality feedback** -- 4 monitoring signals 的 alert 触发 sample
   re-labeling / hard negative mining input
2. **Abuse model retraining schedule** -- adversarial drift signal 决定 retrain
   cadence (weekly default -> daily emergency mode if precision drops > 5pp)

==> Loop closure 是 ML system 与 product 系统的 **continuous feedback** -- 不是
"deploy and forget"，是 "monitoring outputs ARE input to next iteration"。

## 不要这样收尾 (avoid)

- "I think that's all I have." (passive close)
- "I'm done." (no invite)
- "Want to discuss serving in more depth?" (低优先级 fallback -- serving 已 wrap)

## 应该这样收尾 (do)

- 30-sec closing recap (见 verbal_outline col, verbatim 1 段)
- "Are there parts of the design you'd like me to deepen?"
"""


VERBAL_OUTLINE = """\
# Closing 30s Verbatim + Part 5 Mock 节奏 Checklist + 缝合句模板

## Closing 30s recap (verbatim, 可朗读)

"30-sec recap: **viewer-primary top-3 set selection, retrieval bounded (trivial),
2-stage ranking + MMR rerank with hard quota, multi-task MMOE with shallow bias
tower (masked at serve), time + user 双轴 split, tiered feature refresh with shadow
logging for skew defense, list-level A/B with long-horizon north-star holdout,
independent abuse model with tiered action.**"

**关键词密度自查**: 1 句话里出现 set selection / MMR / MMOE / shallow bias tower /
masked at serve / 双轴 split / shadow logging / list-level A/B / long-horizon
holdout / independent abuse model -- 10 个 ML-native 术语，**这才是 recap 的样子**，
不是 "we built a recommendation system that ranks comments"。

## Part 5: 通用 Mock 节奏 Checklist (每次开题前过一遍)

### 5.1 开场 60s checklist

- 一句话 scope statement (input / output / objective / constraint)
- 2-3 个 unique twists，每个带 design implication
- Time plan (15 min 前段 + 25 min 后段)

### 5.2 每段进入时 checklist

- 先说 L1 (the dumbest version)，60 秒内
- 再爬阶梯，每层带 trade-off
- 段末做 4 件事: L1 锚定 / 阶梯展示 / trade-off 表态 / 下段缝合

### 5.3 段末 checkpoint 句式

```
To summarize this section:
 - The simplest version is ___
 - Going one level deeper would be ___ (trade-off: ___)
 - I'm choosing to stop at level ___ because ___
 - This connects to Section ___ where I'll use ___
```

### 5.4 Drift 自查 (每段结束扫一遍)

- 没有在当前段讲下一段的内容
- 没有 reverse-drift 回前面段补丁
- 没有用错位术语 (每个技术词原 paper 解决的是当前问题吗?)
- 没有 dodge 具体问题 (被问 X 答 Y)

### 5.5 List-level 题目 4 特殊提醒 (top-K / carousel / multi-slot)

- 开场显式说 "**this is a set-selection problem, not pure ranking**"
- Metric 段包含 **list-level 指标** (diversity / coverage / set satisfaction)
- Architecture 段**显式区分 ranker / reranker**
- A/B 段用 **list-level metric (any-engagement)** 而非 NDCG/MRR

## 缝合句模板 (每段段末必须落地)

```
[当前段结论 1 句]
==> 下段缝合: [当前段的 X 直接定义/触发/约束下段的 Y]
```

**8 个缝合句示例 (from source verbatim)**:

1. Framing -> Metrics: "这 3 个 twist 每个都会 hook 到下一段的具体 metric 或 guardrail"
2. Metrics -> Labels: "north-star 和 3 个 proxy 直接定义了 label 结构"
3. Labels -> Architecture: "multi-task label 定义了下面 architecture 需要的 head 数量"
4. Features -> Architecture: "comment embedding 喂 L2 ranker 主路；interaction features
   在 DCN 风格 cross layer 里和 user embedding 交叉"
5. Architecture -> Training: "3 head 对应 Section 2 的 3 proxy；shallow tower 实现
   Section 3 承诺的 debias"
6. Training -> Serving: "feature snapshot 策略定义 serving 必须 fetch 什么、多新"
7. Serving -> Monitoring: "shadow logging 也是下面 monitoring 段 online-offline metric
   gap 的 ground truth 来源"
8. Monitoring -> Loop closure: "monitoring outputs ARE input to next iteration"

## ML-native YES / NO 对照表 (本题特有)

### YES (主动用) -- 本题特有 ML-native 词汇

| Category   | Terms (本题高频)                                                                  |
|------------|------------------------------------------------------------------------------------|
| Formulation| set selection / list-level / ranker vs reranker / MMR vs DPP                       |
| Bias       | selection bias / IPS / shallow bias tower / mask-at-inference / shadow logging     |
| Label      | engagement-to-impression ratio / multi-signal weighted / exposed-not-engaged       |
| Sampling   | IPS-weighted / bandit exploration / hard negative mining                           |
| Monitoring | online-offline metric gap / prediction distribution shift / PSI / leading vs lagging |
| Production | tiered refresh / 5-档 cadence / circuit breaker on guardrail breach                |

### NO (被动用) -- avoid 主动 surface

| Category    | Terms (避免 主动)                                                          |
|-------------|----------------------------------------------------------------------------|
| Infra       | QPS / SLA / availability / replication / sharding / fan-out / cache TTL    |
| Storage     | bandwidth / disk / IOPS / index size                                       |
| Surface     | mobile vs web vs API consumer / 多设备适配                                 |

**Why this matters**: list-level 题目主动 surface infra 词汇 = 立刻 down-leveled。
本题 latency budget (p99<200ms) 和 viral peak (100x) 已显式给出，**不要 fishing 更多 NFR**。
"""


CHEAT_SHEET = """\
# 速查表 (Cheat Sheet) — 30s flash review before walking into Top-3 Comments MLSD

## 元结构一图概览

```
Opening 60s (锁三件事)
+- Scope: set-selection top-3, retrieval trivial
+- 3 unique twists with implications:
|   - Comment != item -> text+social fused, commenter sub-entity
|   - Time-bias -> velocity feature + bandit explore
|   - Community health -> guardrail not main objective
+- Time plan: 15 min framing/metric/label/feature + 25 min model+serving+monitoring

Body 段 (Section 1-5.4)
+- L1 (dumbest) -> L2 -> L3 (pick) -> L4 (follow-up)
+- 段末 4 件事: L1 锚定 / 阶梯展示 / trade-off 表态 / 下段缝合
+- 每段每个非显然决策 surface trade-off

Closing 30s (10 ML-native 术语密度 recap)
+- viewer-primary set selection
+- 2-stage + MMR rerank
+- multi-task MMOE + shallow bias tower (masked)
+- 时间 + user 双轴 split
+- tiered refresh + shadow logging
+- list-level A/B + long-horizon holdout
+- independent abuse model + tiered action
```

## 时间锚点 (memorize)

| Time   | Stage                                  | Strong Moment                       |
|--------|----------------------------------------|-------------------------------------|
| 0-1    | Opening 60s (declarative scope)        | **#1** 3 unique twists framing      |
| 1-5    | Section 1 Framing (L1-L4)              | -                                   |
| 5-8    | Section 2 Metrics (NS + proxies + guardrails) | -                            |
| 8-12   | Section 3 Labels (positive ladder + negative selection bias) | **#2** Selection bias 三阶 negative label |
| 12-15  | Section 4 Features (4 象限)            | -                                   |
| 15-21  | Section 5.1 Architecture (funnel + L2 detail) | **#3** Bias Tower + MMR vs DPP |
| 21-25  | Section 5.2 Training (loss / sampling / split / conflict) | -               |
| 25-31  | Section 5.3 Serving (latency budget + tiered refresh + shadow logging) | - |
| 31-35  | Section 5.4 Monitoring + A/B           | **#4** 4 monitoring signals + list-level A/B |
| 35-45  | Closing 30s + Q&A                      | -                                   |

## 4 Strong Moment 预分配表 (类比 sd41 cheat_sheet)

| # | Time   | Theme                                  | Hook (entry phrase)                                         |
|---|--------|----------------------------------------|--------------------------------------------------------------|
| 1 | 0-1    | 3 unique twists framing                | "3 个 unique twists vs generic ranking: comment != item, time-bias..." |
| 2 | 8-12   | Selection bias 三阶 negative label     | "Negative label 是本题核心难点 -- selection bias. 三阶处理..." |
| 3 | 15-21  | Bias Tower + MMR vs DPP                | "Reranker 选择 MMR 不 DPP, n=3 时 DPP 没空间..."             |
| 4 | 31-35  | 4 monitoring signals (leading vs lagging) | "Prediction distribution shift 是比 metric 退化更早的 leading indicator..." |

## 偏好节奏 meta-rules (8 条铁律 -- 与 sd41 共享)

1. **前 60 秒不要问澄清问题** -- 直接 propose scope + 3 twists + time plan
2. **每个开放问题给 60-90 秒回答** -- 不要 30 秒，不要 2 分钟
3. **列完 N 个 bullets 立刻 pick 1 expand** -- 机械规则，不要例外
4. **每个 strong moment 包含 trade-off** -- "X is stronger but costs Y"
5. **每 8-10 分钟主动 zoom-out 或邀请方向选择** -- 避免线性 brain dump
6. **当面试官表情困惑时立刻 park 当前 topic** -- "let me park that, more important is..."
7. **List-level 题目段末必须 list-level metric** -- 不能只说 NDCG/MRR
8. **Wrap 时一定有 top-N risks** -- 这是 E5 边界 signal，也是 E4 strong 必备

## E4 not E5 -- 边界提醒

- DO: confident execution of standard playbook + 1-2 deeper insights
- DO: pick a reasonable model and justify with clear trade-offs (本题 8 个 trade-off matrix)
- DO: identify the top 2-3 risks (selection bias / adversarial drift / list-level diversity collapse)
- DO: show production sense (tiered refresh + shadow logging + circuit breaker)
- DO: drive the conversation forward without getting stuck

- DON'T: invent novel methods (learned DPP kernel for n=3)
- DON'T: over-scope ("2 years out we'd train custom comment-LLM...")
- DON'T: cookbook language ("I'm going to follow standard recommendation pipeline...")
- DON'T: triage email/push/in-app/portal surface 维度 (本题已显式 in-app comments)

## 复用范围 (适用于其他 list-level / set-selection 题型)

本 golden example 的结构 **80% 直接复用** 于:

- **Top-K Search Results ranking** -- query encoder 加进 main tower，list-level metric
  改成 SERP-level satisfaction
- **Multi-slot Ads ranking** -- multi-task heads 加 bid / pCVR + auction logic，
  reranker 用 list-level bid optimization 不是 MMR
- **Carousel recommendation** (E-commerce / video carousel) -- diversity axis 改成
  product category / vertical，hard quota 改成 per-category cap
- **Feed top-N pinned comments** -- 与本题几乎完全一致，只是 n 从 3 改成 5-10

ML 底层框架 (point-wise ranking + list-level reranker + multi-task + bias mitigation
+ time/user 双轴 split + 4 monitoring signals + abuse model independent + tiered
refresh + shadow logging) **不变**，每题独立 twist 投放 Strong Moment #1。

---

## Design Doc 强调话术 (verbatim 用户参考资料第八节, 4 句金句)

**面试 / Design Doc 写作 / Code Review 场合 verbatim 用这 4 句**:

1. **「采用加性 shallow bias tower，结构性强制 relevance / bias 分解」**
2. **「Mask-at-inference 提供干净的反事实排序信号」**
3. **「Shadow feature logging 保证 bias 特征训练/服务分布一致，避免 debias 机制被 skew 破坏」**
4. **「离线 AUC 可能持平甚至微跌，业务指标 (多样性 / 留存 / 新内容曝光) 为真实评估目标」**

**Why these 4 sentences are the killer ending**:

- 第 1 句 = architectural commitment (加性结构 + 容量瓶颈的 inductive bias)
- 第 2 句 = inference correctness (counterfactual semantics 不是工程 hack)
- 第 3 句 = data-layer accountability (skew defense 不是 nice-to-have 是 prerequisite)
- 第 4 句 = **business-metric alignment** -- "AUC 持平甚至微跌仍 ship" 是 E5 边界 signal,
  说明你知道 ML metric 与 product metric 的对应关系，不被 offline number 绑架。
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
    """Run validation checks against the task acceptance criteria."""
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
            errs.append(f"AC2/3 FAIL: column {k} is NULL")
        elif len(v) <= 200:
            errs.append(f"AC2/3 FAIL: column {k} length={len(v)} <= 200")

    total_bytes = sum(len((v or "").encode("utf-8")) for v in prose_cols.values())
    if total_bytes <= 8000:
        errs.append(f"AC3 FAIL: total prose bytes={total_bytes} <= 8000")

    if disp_order != DISPLAY_ORDER:
        errs.append(f"AC4 FAIL: display_order={disp_order}, expected {DISPLAY_ORDER}")

    if ANCHOR_FR_NODE not in (architecture or ""):
        errs.append(f"AC5 FAIL: anchor fr-node path not in architecture col")
    if ANCHOR_FR_NODE not in (prod_cons or ""):
        errs.append(f"AC6 FAIL: anchor fr-node path not in production_constraints col")

    design_doc_phrases = [
        "采用加性 shallow bias tower",
        "Mask-at-inference 提供干净的反事实",
        "Shadow feature logging 保证 bias 特征",
        "离线 AUC 可能持平甚至微跌",
    ]
    for phrase in design_doc_phrases:
        if phrase not in (cheat or ""):
            errs.append(f"AC7 FAIL: design-doc phrase {phrase!r} not in cheat_sheet col")

    if "Meta MLSD Golden Example" not in (subtitle or ""):
        errs.append("subtitle missing 'Meta MLSD Golden Example' substring")

    if not chash:
        errs.append("content_hash is empty")
    if not upd_at:
        errs.append("updated_at is empty")

    cur.execute(
        "SELECT COUNT(*) FROM system_designs WHERE display_order = ?",
        (DISPLAY_ORDER,),
    )
    cnt = cur.fetchone()[0]
    if cnt != 1:
        errs.append(
            f"display_order={DISPLAY_ORDER} has {cnt} rows (expected 1)"
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

    print("\n[DONE] all ACs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
