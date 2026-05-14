"""Seed: T-P0-837 [Meta-MLSD A] Reels Golden Example -> system_designs.

INSERTs (or idempotently updates) the canonical Meta MLSD golden example as
``system_designs(slug='meta-reels-golden')``, drawer-reachable via
``sd://meta-reels-golden``.

T-P1-875 archetype migration (2026-05-13): document_archetype migrated from
``structured_reference`` (10-field shape, ~45KB across overview/architecture/
dataflow/formulas/production_constraints/tradeoffs/defense/verbal_outline/
cheat_sheet) to ``oral_narrative``. Per the new archetype's contract in
``schemas/meta_mlsd_canonical.yaml`` (``document_archetypes.values.oral_narrative``):

  - ``dataflow`` carries a single continuous 第一人称 45-min 口播稿 (8 sections).
  - ``overview`` / ``formulas`` / ``cheat_sheet`` are slim anchors.
  - ``architecture`` / ``production_constraints`` / ``tradeoffs`` / ``defense``
    / ``verbal_outline`` are NULL by design -- their content lives inlined
    in the dataflow narrative (立场 + trade-off + Strong Moment + verbatim).

Rationale: structured_reference shape spread the same Reels insights
(multimodal twist / ambiguous middle label / IPS-as-acquisition / hard-filter
compliance) across overview -> architecture -> dataflow -> defense fields,
each restating the others. Per user (Discord 2026-05-13 22:39 + the third-party
review in msg 1504368694875394158) the new shape consolidates everything
into one continuous oral-recital script, satisfying 4 criteria (causal chain
complete / first-person speakable / trade-off has立场 / has defense + twist)
via 因果链 + 立场+trade-off + twist 在 body 兑现 三原则.

The 4 criteria were mechanically verified against the new dataflow before
this migration -- see PROGRESS.md 2026-05-13 22:55 + Discord msg
1504369692121239665 (verification report).

Idempotent: re-running upserts in place by ``slug``. Sentinel-based UPSERT
keyed on ``slug='meta-reels-golden'``. Architecture-shape fields (5 NULLed)
remain NULL on re-run; if a structured_reference seed is later re-run against
the same row, it would re-populate them -- but the canonical archetype
declaration in ``meta_mlsd_canonical.yaml`` means the audit would flag that
as a regression.

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
    "Meta MLSD Golden Example — 第一人称完整 45min 口播稿 "
    "(因果链 + 立场+trade-off + twist 在 body 兑现 三原则). "
    "适用于 Reels / Feed / Notification / Friend-rec / Ads 等 Meta MLSD 题型 "
    "(80% 结构复用). 方法论 (Strong Moment 调度, ML-native vocab, 8 meta-rules, "
    "E4/E5) 在 cd://96。"
)
DISPLAY_ORDER = 130
SOURCE_PATH = "docs/prep/meta_mlsd_2026-05-11/source_01_pacing_golden.md"

# T-P1-875: this seed produces an oral_narrative archetype document. See
# schemas/meta_mlsd_canonical.yaml > document_archetypes.values.oral_narrative.
DOCUMENT_ARCHETYPE = "oral_narrative"


OVERVIEW = """\
# Reels Home Feed — 45min Golden 口播稿

按"因果链 + 立场+trade-off + twist 在 body 兑现" 三原则写成的完整第一人称口播稿。完整 8 段台词在 `dataflow` tab; multi-head label schema 公式在 `formulas`; 数字 anchor + firm-claim register 在 `cheat_sheet`。方法论 (timing skeleton, Strong Moment 调度, ML-native vocab YES/NO, 8 meta-rules, E4/E5 boundary) 在 `cd://96` 主 hub, 此 row 只承载 Reels 这一题的 solution。

两条 driving twist 在 framing 段就 declarative surface, 后续每个 component 兑现:

1. **Multimodal lifecycle** — UGC 短视频, 文本稀疏, 内容理解不能靠 metadata; pretrained video/audio/text encoder fused → 256-dim, upload-time 算一次, 季度 refresh。把 content understanding cost 从 serving path 剥离。
2. **Session dynamics** — Reels 是连续消费, within-session fatigue / drift / diversity collapse 是 retention 主杀手; 需 request-time session-context features + session-aware ranker。

整体方案: 多路 retrieval (60/20/20) → DLRM multi-task ranking → whole-page rerank, multimodal embedding 在 upload 时算好缓存。"""


DATAFLOW = """\
# 完整 45min 口播稿 (第一人称, 8 段连续)

> Section 标题只是导航用, 真讲的时候是连续说下来的。每段串因果链, 每立场挂 trade-off, framing 立的两个 twist (multimodal lifecycle / session dynamics) 在 body 里兑现。

---

## 开场 · Framing

"好, 这道题我把它 formulate 成一个 Reels home feed 的推荐问题——给定一个用户和他当前的浏览 context, 从我们的视频库里返回一个有序的 feed 列表。

我先做几个假设, 确认一下边界。第一, user 这一侧, 我假设这是已登录用户为主的场景, 因为推荐高度依赖历史行为, 未登录的匿名流量我会走一套退化的、基于 trending 和 context 的逻辑, 但不是这道题的主线。第二, 规模上, 我假设是亿级 DAU、百万级 QPS、内容库大概一亿量级, 端到端 latency SLO 我按 p99 200 毫秒来设计。

然后是 input、output 和 objective。这里我想先纠正一个我自己容易说顺嘴的地方——视频库是 corpus, 它不是 model 的 input。一次 request 真正的 model input, 是 user feature、context feature, 加上候选 item 的 feature 这三组东西。

objective 上, 我认为这个问题 user-end metric 是要明确高于 biz metric 的。我希望优化的是中长期的用户价值——比如 7 日 retention、session 时长、人均观看时长这些。而 revenue、还有内容生态健康度, 我把它们放在 guardrail 这一侧。这里我要明确一点: guardrail 里最重要的其实不是 revenue, 是 integrity——NSFW、违规内容的 violation rate, 这是 UGC 平台的大头; 再加上 creator-side 的健康度和 diversity。我特意不把 NDCG、MRR 放进 guardrail, 因为那是我自己系统的 offline ranking metric, 不是一个独立的约束。

output 这一侧, 我们没有一个直接的 ground truth label, 所以要找 proxy。我会同时建模两类信号: 一类是 contextualized 的完播率, 一类是观看时长 ratio。两个一起用是有意为之的——单看完播率会系统性偏向短视频, 单看时长会偏向长视频, 两个一起、再把 duration 本身作为 feature 和 evaluation slice, 就能把这个 confounder 平衡掉。负向信号比如 early-skip 我也会用, 但具体怎么设计我想留到 label section 展开。

最后说 twist——这道题和一个传统 recSys 不一样的地方, 我认为有三点。第一, Reels 是 multimodal 的 UGC, 文本信号稀疏, 所以内容理解不能靠 metadata, 得做 content understanding。第二, 也是我认为最 signature 的一点, Reels 的消费是 session-based、连续的——用户一次刷几十个, session 内的 fatigue、兴趣漂移、diversity 塌陷, 是 retention 的主要杀手, 这个必须显式建模。第三, 推荐天然有 exposure bias, 我们的 label 全是 conditioned on 我们推了什么, 需要 debias。

整体方案就是一个标准的两阶段漏斗: 多路 retrieval、multi-task ranking、whole-page rerank, content embedding 在 upload 时算好缓存。

这是我的 framing。接下来 data 和 label、retrieval、ranking、serving 这几块, 你想我先深入哪一块? 还是按顺序走?"

---

## Data & Label

"好, 那我从 data 和 label 开始, 因为我觉得这块对 Reels 来说是最 non-trivial 的。

label 设计的核心张力, 我认为是 signal density 和 bias 之间的权衡——越显式的信号越准但越稀疏, 越 implicit 的越多但越脏。所以我分层来看。

最显式的是用户主动反馈: 正向是 like、share、collect、follow, 负向是 report、dislike。这类 signal 高精度, 但非常 sparse, 类别极度不平衡。

往下一层是 watch-based 的信号, 这其实是 Reels 的主 label, 而且它不是二元的, 是个回归信号——normalized watch ratio, 定义成观看时长除以视频时长, capped 在 1。一定要 normalize, raw 时长会系统性 over-weight 长视频。

负样本这一侧, 我的主线是 in-session 的 early-skip——用户在前 2 到 3 秒、或者完播率低于 20% 就划走。这是 Reels 特有的、天然的 hard negative, 它免费、量大, 而且因为是我们 surface 过的, 它至少是相对无偏的。这一点我想强调, 因为它比从外部挖 hard negative 要干净得多。

这里有一个 nuance 我想专门提一下——ambiguous middle。一个用户看了 50% 然后划走, 他既不是 hard negative 也不是 strong positive, 是真的 ambiguous。我的处理是: 在 watch-ratio 这个 head 上把它当弱正样本, 但在 early-skip 这个 head 上直接把它排除掉。强行给 ambiguous 数据打一个二元 label, 只会往训练里加噪声。

再往下, 从我们根本没 surface 过的内容里, 可以采样少量 easy negative。但我要点明一点——这些 easy negative 本身是 biased 的, 把没推过当成用户不喜欢, 这恰恰就是 exposure bias 的源头。所以用它的时候必须配合 sampling 上的修正, 或者用 exploration 收集的数据来兜底。更激进一点, 还可以用全局采样、甚至 LLM-as-judge 去挖一些 false negative, 但那个成本高、会引入 judge 自己的 bias, 我会把它定位成一个可选项, 不是主线。

最后, duration 是几乎所有 engagement label 的 confounder, 5 秒的 loop 天然比 60 秒的好完播。所以 duration 对我来说既是 feature input, 又是 evaluation 时必须切的 slice。"

---

## Features

"feature 这块框架比较套路, 我按 user、content、context、cross 四类来分, 但 Reels 的关键是要把 session 动态这一类从 cross 里单独拎出来。

user feature, 我的主力其实是用户的行为序列建模出的 embedding。demographic——性别、职业这些——我反而会很谨慎, 它预测力弱、而且合规敏感, 我把它降级成 cold-start 时的兜底信号, 不是主力。另外像用户来了多久、有没有我们内部的 level 和 merit 体系, 这类我也归在 user 这一侧, 没有争议。我整体是从一个 triage 的视角来组织 user feature, 不是一味堆 IID 数据。

content feature, 常规的是 engagement 统计量——曝光、CTR、完播率、各种 count。但这里有个问题: 这些统计量对冷启动 item 是全空的。所以 content 这一侧必须包含 upload 时就算好的 multimodal embedding, 否则新视频没有任何内容表征。

context feature 比较直接: time of day、device、network、用户是怎么进到这个视频的。

cross feature, 我想拆成两类讲。一类是 lifetime 的行为 cross——用户和 creator、用户和 topic 的 affinity, 这种我靠 DCN 这样的结构去显式建模 feature interaction。另一类, 也是我想专门强调的, 是 in-session state——这个 session 内已经看了几个、到目前为止的平均完播率、swipe rate、最近 K 个 item 的 topic 分布。这一类必须 request-time 现算, 它是处理 session 内 fatigue 和 drift 的唯一抓手。我前面把 session-based 消费立成了核心 twist, 这组 feature 就是它在 feature 层的落地。

关于 debias, 我打算集中放在 feature 和 model 这一侧来处理。具体做法是把 position、device 这类 bias feature 放进一个独立的 shallow bias tower, 训练的时候正常用, serving 的时候把这个 tower 的输入置 0。这个比 training-time 的 IPS reweighting 更稳、更好 ship。但我要补一个边界——这个 bias tower 修的是已经 surface 过的数据内部的 selection bias, 它修不了根本没被 surface 那一类内容, 所以它是必要但不充分的, 完整的答案还得靠 exploration 配合。"

---

## Model

"model 我分 retrieval 和 ranking 两段。

retrieval 之前, 我想先花一点时间对比一下 retrieval 范式和 generative 范式, 因为 Reels 其实挺适合 generative 的。retrieval-based 的优势是对 hot item 的判断更精细, ID memorization 够、精度高, 而且 candidate pool 大、有 fallback 余地。generative 范式的优势我想说准确——它的强项是不需要维护 ANN 索引、检索逻辑参数化进了模型, 以及 autoregressive 解码天然建模 item 之间的序列依赖, 还有 scaling law。这里我要纠正一个常见的说法: generative 对冷启动其实不是优势, 反而是它的弱点——它生成的是 semantic ID, 一个全新的、零交互的 item, 它的 SID 可能还没进 codebook, 模型不会去生成它。所以冷启动这两个范式都不天然解决, 这个我留到后面单独讲。

虽然 Reels 很适合 generative, 但我 v1 会推荐 retrieval-based, 理由是已有系统兼容性、latency 和 compute budget。代价是 generative 的序列建模优势我暂时拿不到, 所以我会把 generative 明确定位成 next-iteration 的演进方向, 而不是 v1。

具体的 retrieval, 我会做多路召回: 一路是 ANN two-tower 的个性化召回, 这是主力; 一路是基于 history viewed tag 和 query 的 indexing-based 召回; 再加 diversity 相关的召回路。two-tower 的训练用 contrastive, 负样本是 in-batch negative 加上从 early-skip 里挖的 hard negative。in-batch negative 免费、coverage 广, 但它会偏向 popular item, 所以我会用 log-Q correction 来修这个 popularity bias。

ranking 我做两阶段, 而且我想强调 L1 和 L2 不是两个无关的模型, 它们是同一个建模思路上的成本梯度。L1 的职责是 storage-local、便宜、把几千个候选快速砍到几百个, 只要别误杀 L2 本来会高分的 item 就行。我的背景是做大规模 search 的, 自然的分层逻辑是 L1 侧重简单的一两阶 crossing、L2 做精细的 interactive 建模。具体到 Reels, L1 我会用一个 distilled 的小双塔加 MLP——它本质上听起来就像一个输入受限的 DLRM, 和 L2 共享 feature、用蒸馏对齐打分分布。我特意不用 GBDT, 不是因为 GBDT 过时, 是因为 Reels 的主力信号是高维的 ID embedding 和 multimodal embedding, GBDT 吃不动这类输入。L1 我默认压到 2 阶 cross。

L2 就放开了, 用 DLRM 加 DCN, cross 阶数堆到三四阶, 输出 100 到 200 个结果。具体需要多少阶 crossing, 我会给一个有先验的起点再用 ablation 验证——而且 ablation 要看的是 L1 加 L2 串起来的端到端 recall, 不是 L1 单层的精度。

最后是 reranking, 在 whole-page 这一层。这里我想把两类机制分清楚: 合规、NSFW 这类是 hard filter, 二元 disqualify, 直接 mask 掉, 它不是 rerank objective 里的一个软目标——把 compliance 当 soft loss term 是个 category error。diversity 这类才是 soft 的, 用 MMR 或 DPP, 是个 trade-off 不是 cutoff。如果 hard filter 砍得太多导致候选不够, 我会做 backfill, 但 backfill 有质量梯度——优先从 L2 的次高分补, 其次 trending, 最后才是 category popular。一次 push 我觉得 10 到 25 个 feed 就够了。"

---

## 冷启动 (承接 model)

"前面提到冷启动两个范式都不天然解决, 我在这里收一下。

item 冷启动, 我的主线是 content-based——multimodal embedding 在 upload 时就有, 新视频靠它进 retrieval; engagement 统计量缺失时, fallback 到 category 或 creator 的 average, 而不是 site average, site average 太糊。

在这个之上, 我会留一个结构性的补充: retrieval 里专门有一路 fresh-content channel, 再给每个 session 一个小比例、大概 5% 的 exploration 预算, 但要 gated by 质量过滤, 防止低质内容套利这个预算。

user 冷启动, 可以在 onboarding 时让新用户过一个 diverse 的内容集, 用早期 engagement 当相对无偏的 preference 信号, 但我会让这个流程保持轻量。bandit 我知道是个选项——可以用 contextual bandit 来平衡 explore 和 exploit——但我会点到为止, 不展开。"

---

## Evaluation

"evaluation 我分三层。

offline, 我先看 per-head 的 metric——watch-ratio 这个回归 head 看 weighted NDCG, engagement 和 early-skip 这两个二元 head 看 AUC。关键是所有 metric 都要按 duration bucket 和用户 segment 切片, 因为 duration 是 confounder、新老用户的分布也不一样。

online A/B, 我想强调一个 Reels 特有的陷阱——实验单位必须是 user 或 session 级, 不能是 item 或 impression 级。因为 session 内 item 之间是互相影响的, impression 级随机化会污染。看的指标也要是 session-level 的: session 时长、return rate、day-N retention。

第三层是 long-term holdout, 30 天以上, 抓那些短期 A/B 看不到的东西——filter bubble 收窄、creator 生态效应、fatigue 累积。

我还想 flag 一个点: offline 和 online 的对齐问题。offline NDCG 涨不一定 online retention 涨, 这个 correlation 我会显式追踪, 漂了就重新校准 offline metric。"

---

## Serving / Logging

"serving 和 logging, 我知道这不是 ML SD 考察的最大重点, 所以我给你几个我最在意的点, 不展开。

我最关心的是 train-serving skew。首选的根治方案是 serving-time 的 feature snapshot——serving 当下把喂给模型的 feature 值原样落盘, 训练直接用这份。如果因为 budget 原因做不到, 退一步是只做 query-request logging、feature 离线重建, 但那样必须配 offline replay 来校验重建的偏差。新 feature 上线前, 走 shadow logging, 先 log 不打分, 观察 feature drift。

serving 本身, 我沿用 framing 里提的 push-pull——active user 走 batch precompute 的 cache 拿低延迟, 其余 fallback 到 pull, 同时一条 online 增量路径负责没有任何 engagement 历史的新内容。

部署形态上, retrieval 和 L1 是 distributed、sharded 的, index 按 item 分片, 本地出 top candidate 再 scatter-gather 聚合; L2 是集中式的, 因为候选规模到这里已经塌缩了两三个数量级。这也正好呼应前面说的 L1 便宜、storage-local。"

---

## Wrap

"我 zoom out 总结一下, 然后说三个我最担心的 risk。

整体是一个两阶段的 retrieval 加 ranking 系统, 带 multimodal 内容理解、multi-task ranking head、session-aware feature, exposure bias 靠 bias tower 加 exploration policy 来缓解, evaluation 覆盖 offline、online、long-term 三层。

三个 risk。第一, exposure bias 复利的速度可能快过我们 mitigation 的速度, 5% 的 exploration 预算不一定够——我会监控 served diversity, 跌破阈值要有 circuit breaker。第二, multi-task 的 loss 权重会随数据分布漂移, 所以我的 retrain pipeline 要重新调 head 权重, 不是固定组合下重训。第三, 也是最重要的——watch time 涨但 retention 跌, 这是 clickbait 和 rage content 在 gaming 我们的 proxy, 这个最重要的 alarm 靠 long-term holdout 来抓。

这些就是我的设计, 有哪一块你想让我再深入吗?"
"""


FORMULAS = """\
# Label Schema 公式 (口播稿 Data&Label 段对应的形式化)

> 口播稿原文在 `dataflow` tab; 此处只放 watch-ratio / strong-positive / early-skip 三头的精确定义 + duration confounder + 权重组合方式, 面试官追问公式时打开。

## Multi-head label 定义

| Label | 定义 | Head type | 用途 |
|-------|------|-----------|------|
| `watch_ratio` | `min(watch_time / video_duration, 1.0)` | regression / bucketed classification | Reels 主 label; 一定 normalize, raw 时长 over-weight 长视频 |
| `strong_positive` | `1 if (like ∨ comment ∨ share ∨ follow ∨ save) else 0` | binary | 显式正反馈; sparse high-precision, 类别 imbalance 严重 |
| `early_skip` | `1 if (swipe_at < 2.5s ∨ watch_ratio < 0.2) else 0` | binary | implicit hard-negative; Reels 特有的天然 hard negative |

## Ambiguous middle 处理 (关键 nuance)

定义 `ambiguous_middle = (0.2 ≤ watch_ratio ≤ 0.5)`:
- `watch_ratio` head: 当弱正样本 (label 直接用 watch_ratio 值, 没特殊处理)
- `early_skip` head: 直接从训练集中排除 (不打 0/1 二元 label)

> 强行二元化 ambiguous middle 只往训练里加噪声。

## Duration confounder

duration 既是 **feature input**, 又是 **evaluation slice**。所有 offline metric 必须按 duration bucket 报: `[0-5s, 5-15s, 15-30s, 30-60s, 60s+]`。

## 权重组合 (post-train tunable)

```
final_score = w_1 · p̂_watch_ratio + w_2 · p̂_strong_positive + w_3 · (1 - p̂_early_skip)
```

权重 `w_k` post-train tunable — 调 engagement-vs-quality trade-off 不需要 retrain。tuning 用 Pareto search on offline metrics (不用 GradNorm — head 不强 competitive, Pareto search 可 audit 易 ship review)。

## Sharing strategy

shared backbone (sparse-emb + dense-MLP + DCN) → 3 个 head-specific top-MLP:

```
[shared backbone]
        │
        ├─── [head 1: watch_ratio top-MLP]    (regression)
        ├─── [head 2: strong_positive top-MLP] (binary)
        └─── [head 3: early_skip top-MLP]      (binary)
```

watch-ratio 与 strong-positive correlated 足够 benefit from 共享表征; early-skip 用同一 backbone 是因为 backbone capacity 足够 absorb 三头的分布差异。"""


CHEAT_SHEET = """\
# 30-sec pre-walk-in checklist — Reels-only

> 方法论 (timing skeleton, 元结构, 8 meta-rules, E4/E5 boundary, drift recovery vocab) 在 `cd://96` §1 / §5 / §6 / §8。此处只放 Reels 特有的 anchor 数 + firm-claim register, 进面前 30 秒过一遍。

## 数字 anchor (说出来时声音里就有数)

- **60/20/20**: 多路 retrieval 切分 (personalized / trending / diversity)
- **5% per session**: exploration impression 预算
- **256-dim**: multimodal content embedding 维度; 季度 refresh
- **20% 完播 或 <2.5s**: early-skip 定义 (Reels 特有 hard-negative)
- **30+ days**: long-term holdout 抓 filter bubble / creator 生态 / fatigue
- **~100M items, HNSW / ScaNN, 单数字 ms p99**: retrieval/serving 规模 anchor
- **p99 200ms**: 端到端 latency SLO
- **10-25 items per push**: 一次 feed 返回长度

## Firm-claim register (整场至多说 1 次)

- "**视频库是 corpus, 不是 model input**——一次 request 的 input 是 (user, context, candidate item) 三组 feature。" (开场 framing 立场)
- "**单看完播率偏短视频, 单看时长偏长视频; 一起用 + duration 当 slice 平衡 confounder。**" (Data 段 watch-ratio 立场)
- "**ambiguous middle 在 watch-ratio head 当弱正、在 early-skip head 直接排除——强行二元化是加噪声。**" (Data 段 label nuance)
- "**bias tower 修的是 surface 过的数据内部的 selection bias, 修不了根本没 surface 的——必要但不充分, 完整答案还得靠 exploration。**" (Features 段 debias 边界)
- "**generative 对冷启动不是优势, 反而是弱点——新 item 的 SID 可能还没进 codebook。**" (Model 段范式对比纠错)
- "**L1 不用 GBDT 不是因为 GBDT 过时, 是因为 Reels 主力是高维 ID + multimodal embedding, GBDT 吃不动。**" (Model 段 L1 立场)
- "**compliance 是 hard filter 不是 soft loss term——把 compliance 当 soft loss 是 category error。**" (Model 段 rerank 立场)
- "**A/B 必须 user/session 级, 不能 item/impression 级——session 内 item 互相影响, impression 级随机化会污染。**" (Eval 段 Reels 陷阱)
- "**train-serving skew 首选 serving-time feature snapshot 根治, 退到 offline 重建必须配 replay 校验。**" (Serving 段)
- "**watch time 涨但 retention 跌——这是最重要的 alarm, 靠 long-term holdout 抓。**" (Wrap 段 risk #3)

## 复用范围

此 row 的 2-stage + multi-task + 60/20/20 + 3-层 eval 是 Reels carve-up。Feed / Notification / Friend-rec / Ads / Top-3 Comments 的 mapping 见 cd://96 hub + sibling sd-golden (`sd://meta-top3-comments-golden`, `sd://meta-weapon-ads-golden`, `sd://meta-friend-rec-golden`)。"""


# T-P1-875: oral_narrative archetype NULLs these 5 fields. Their content lives
# inlined in DATAFLOW (the 8-section 口播稿). Validation in
# scripts/audit_meta_mlsd_3rule.py respects the archetype declared on the
# instance in schemas/meta_mlsd_canonical.yaml.
ARCHITECTURE: str | None = None
PRODUCTION_CONSTRAINTS: str | None = None
TRADEOFFS: str | None = None
DEFENSE: str | None = None
VERBAL_OUTLINE: str | None = None


def _now() -> str:
    """ISO-8601 UTC timestamp with seconds precision."""
    return datetime.now(UTC).isoformat(timespec="seconds")


def _content_hash(payload: dict[str, str | None]) -> str:
    """Stable hash over the canonical content fields (NULL contributes empty string)."""
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
    """Insert or update the row, writing NULL for archetype-nullable fields."""
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
    """Archetype-aware seed-side validation.

    For oral_narrative: verify the 4 contracted fields populated, the 5 NULL
    fields actually NULL, content_hash present, and the row carries the
    expected slug/title/display_order. Deep semantic checks (R-3RULE-* /
    R-NARRATIVE-* / R-CHAR-range / R-DRAWER-no-sd-drawer) live in
    scripts/audit_meta_mlsd_3rule.py and are the canonical post-seed gate.
    """
    errs: list[str] = []

    cur.execute(
        "SELECT id, slug, title, subtitle, display_order, overview, "
        "architecture, dataflow, formulas, production_constraints, "
        "tradeoffs, defense, verbal_outline, cheat_sheet, content_hash, "
        "updated_at FROM system_designs WHERE slug = ?",
        (SLUG,),
    )
    rows = cur.fetchall()
    if len(rows) != 1:
        errs.append(
            f"AC1 FAIL: expected exactly 1 row for slug={SLUG}, got {len(rows)}"
        )
        return errs

    (
        rid, slug, title, subtitle, disp_order, overview, architecture,
        dataflow, formulas, prod_cons, tradeoffs, defense, verbal, cheat,
        chash, upd_at,
    ) = rows[0]

    # Populated-fields contract for oral_narrative.
    populated = {
        "overview": (overview, 200),
        "dataflow": (dataflow, 4000),
        "formulas": (formulas, 200),
        "cheat_sheet": (cheat, 200),
    }
    for col, (body, floor) in populated.items():
        if body is None or len(body) < floor:
            errs.append(
                f"AC2 FAIL: column {col} length={len(body or '')} < {floor} "
                f"(oral_narrative populated-floor)"
            )

    # NULL-fields contract for oral_narrative.
    nulled = {
        "architecture": architecture,
        "production_constraints": prod_cons,
        "tradeoffs": tradeoffs,
        "defense": defense,
        "verbal_outline": verbal,
    }
    for col, val in nulled.items():
        if val is not None and val != "":
            errs.append(
                f"AC3 FAIL: column {col} expected NULL (oral_narrative) but "
                f"got length={len(val)}"
            )

    if "Meta MLSD Golden Example" not in (subtitle or ""):
        errs.append("AC4 FAIL: subtitle missing 'Meta MLSD Golden Example'")
    if not chash:
        errs.append("AC5 FAIL: content_hash empty")
    if not upd_at:
        errs.append("AC5 FAIL: updated_at empty")

    cur.execute(
        "SELECT COUNT(*) FROM system_designs WHERE display_order = ?",
        (DISPLAY_ORDER,),
    )
    cnt = cur.fetchone()[0]
    if cnt != 1:
        errs.append(
            f"AC6 FAIL: display_order={DISPLAY_ORDER} has {cnt} rows (expected 1)"
        )

    print(f"[OK] row id={rid} slug={slug}")
    print(f"     title={title[:60]}...")
    print(f"     archetype={DOCUMENT_ARCHETYPE}")
    print(f"     display_order={disp_order}")
    print(
        f"     populated: overview={len(overview or '')} dataflow={len(dataflow or '')} "
        f"formulas={len(formulas or '')} cheat_sheet={len(cheat or '')}"
    )
    print(
        f"     nulled: architecture={'NULL' if architecture is None else len(architecture)} "
        f"production_constraints={'NULL' if prod_cons is None else len(prod_cons)} "
        f"tradeoffs={'NULL' if tradeoffs is None else len(tradeoffs)} "
        f"defense={'NULL' if defense is None else len(defense)} "
        f"verbal_outline={'NULL' if verbal is None else len(verbal)}"
    )
    return errs


def main() -> int:
    """CLI entrypoint."""
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

    print("\n[DONE] oral_narrative archetype seed: all ACs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
