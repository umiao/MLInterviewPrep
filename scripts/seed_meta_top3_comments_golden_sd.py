"""Seed: T-P0-853 / T-P1-881 [Meta-MLSD] Top-3 Comments Golden -> system_designs.

INSERTs (or idempotently updates) the canonical Meta MLSD Top-3 Comments
golden example as ``system_designs(slug='meta-top3-comments-golden')``,
drawer-reachable via ``sd://meta-top3-comments-golden``.

T-P1-881 archetype migration (2026-06-17): document_archetype migrated from
``structured_reference`` (10-field shape, ~54KB across overview/architecture/
dataflow/formulas/production_constraints/tradeoffs/defense/verbal_outline/
cheat_sheet) to ``oral_narrative``, mirroring the sd41 (reels) golden template
(T-P1-875) and the sd-weapon/sd-friend minimal-A mirrors (T-P0-894/895). Per
``schemas/meta_mlsd_canonical.yaml`` (``document_archetypes.values.oral_narrative``):

  - ``dataflow`` carries a single continuous 第一人称 45-min 口播稿 (8 sections).
    This 10504-char narrative is the made golden (authored into the DB ahead of
    this migration); this seed captures it as the source of truth (Invariant 3).
    The prior structured-shape DATAFLOW (6378 chars) is superseded.
  - ``overview`` / ``formulas`` / ``cheat_sheet`` are slim anchors (kept from the
    structured seed -- they already read as oral anchors).
  - ``architecture`` / ``production_constraints`` / ``tradeoffs`` / ``defense``
    are NULL by design -- their content (2-stage ranking + bias tower + MMR-vs-DPP
    + selection-bias label + serving/skew + 8 tradeoffs + 4 Strong Moments) lives
    inlined in the dataflow 口播稿.
  - ``verbal_outline`` is NULLed here and re-populated by
    ``seed_meta_meta_top3_comments_golden_verbal_outline.py`` (T-P0-893); run that
    verbal seed AFTER this main seed. It is a nullable field for oral_narrative.

The 4 oral_narrative criteria (causal chain complete / first-person speakable /
立场 + trade-off / twist 在 body 兑现) plus the section-level 3-rule were
mechanically verified against the dataflow before this migration; the canonical
post-seed gate is ``scripts/audit_meta_mlsd_3rule.py`` (expects 0 findings
sd41-44).

Idempotent: re-running upserts in place by ``slug``. Sentinel-based UPSERT
keyed on ``slug='meta-top3-comments-golden'``. The 5 NULLed fields remain NULL
on re-run; the canonical archetype declaration in ``meta_mlsd_canonical.yaml``
means the audit flags any structured-shape re-population as a regression.

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

# T-P1-881: this seed produces an oral_narrative archetype document. See
# schemas/meta_mlsd_canonical.yaml > document_archetypes.values.oral_narrative.
DOCUMENT_ARCHETYPE = "oral_narrative"


OVERVIEW = """\
# Top-3 Comments under a Post -- 45min Golden Walkthrough

This golden walks one verbatim 45-minute interview for **Top-3 Comments under a Post**: a viewer-primary set-selection problem where retrieval is trivially bounded by the post's own comment pool, so the design lives entirely in **ranking + list-level reranking**. The unique angle is that **three intrinsic twists** -- comment-is-not-an-item, early-comment time-bias, and community-health-as-guardrail -- drive almost every downstream decision, and the answer is to put all three on the table inside the first 60 seconds, then revisit each as a Strong Moment later. Methodology (timing skeleton, ML-native vocabulary YES/NO, 8 偏好节奏 meta-rules, E4/E5 boundary) lives in `cd://96`; this row owns only the solution.

## Twist 1 -- Comment is not a generic item

Comments are ultra-short text whose authorship is a user-graph node, so the dominant signal is social, not text. **I pick** text + social fused representation (caption / hashtag-style mini-BERT for the body, commenter sub-entity embedding for identity, viewer x commenter follow / past-engagement as cross features), feeding the L2 ranker's main tower. Costs: an extra commenter-side embedding pipeline maintained alongside the post-side index. **Switches to** pure text two-tower retrieval only if the post pool exceeds ~10k comments per post -- not the in-feed regime. This is where the "ranker beats two-tower because ranker can see viewer x commenter interaction terms" claim pays off.

## Twist 2 -- Early-comment time-bias

Comments posted in the first minutes of a post's life accumulate disproportionate impressions, so raw engagement counts confound time-of-arrival with quality. **I pick** **engagement velocity (rate, not count)** as the time-debiased label and feature, plus a **5% per-session bandit exploration budget** to surface late-arriving comments. Costs: streaming engagement-rate compute (1-5 min cadence) and a UX cost of late-comment exposure. **Switches to** simple count-based ranking only if velocity infra is unavailable in week 1, but the time-bias mitigation is the twist this Strong Moment hosts.

## Twist 3 -- Community-health is a guardrail, not a head

Toxicity / abuse / harassment are disqualifying, not "less engagement". **I pick** an **independent abuse model + toxicity hard filter pre-ranker** (NOT shared weights with the engagement ranker), with tiered action (hard filter for confident, hard demote for uncertain). Costs: a second model trained on weekly retrain cadence to fight adversarial drift. **Switches to** soft loss term only if abuse model precision collapses below 0.8 -- but treating compliance as a loss term is a category error.

## 4 Strong Moment slots (pre-allocated, do NOT improvise)

The 4 slots fire at fixed times. **Slot #1 (0-1)** carries the 3-twist framing — "set-selection not pure ranking" + 3 twists + 15/25 time plan. **Slot #2 (8-12)** carries the selection-bias 三阶 negative label — IPS-weighted exposed-not-engaged + 5% bandit unexposed + hard-neg mining. **Slot #3 (15-21)** carries the bias tower + MMR-vs-DPP architectural pair — shallow additive bias tower with mask-at-inference plus MMR with hard quota across 3 axes. **Slot #4 (31-35)** carries the 4 monitoring signals (leading vs lagging) — prediction distribution shift earlier than engagement metric, plus list-level A/B.

| # | Time   | Theme                                  | Top-3-Comments-specific twist anchor                                            |
|---|--------|----------------------------------------|---------------------------------------------------------------------------------|
| 1 | 0-1    | 3 unique twists framing                | "set-selection not pure ranking" + 3 twists + 15/25 time plan                   |
| 2 | 8-12   | Selection-bias 三阶 negative label     | IPS-weighted exposed-not-engaged + 5% bandit unexposed + hard-neg mining        |
| 3 | 15-21  | Bias Tower + MMR vs DPP                | shallow additive bias tower + mask-at-inference + MMR with hard quota across 3 axes |

The full first-person 45-min 口播稿 now lives in the **`dataflow`** tab -- this row is an **oral_narrative** archetype, so the solution body is consolidated there rather than split across architecture / tradeoffs / defense (those columns are intentionally NULL). **`formulas`** holds the label schema; **`cheat_sheet`** holds the Top-3-Comments quantification anchors + firm-claim register; **`verbal_outline`** holds the Top-3-specific entry phrases. Methodology (rhythm rules, vocab YES/NO, E4/E5 line) belongs in `cd://96`.
"""


DATAFLOW = """\
# 完整 45min 口播稿 (第一人称, 8 段连续)

> 第一人称连续口播稿, 8 段串下来。Section 标题只是导航用, 真讲的时候是连续说下来的。每段串因果链, 每立场挂 trade-off。framing 立的 3 个 twist (comment 不是 item / early-comment time-bias / community health 是 guardrail) 在 body 里逐个兑现。方法论层 (timing skeleton、Strong Moment 调度、ML-native vocab、8 meta-rules、E4/E5 boundary) 不在这份脚本里, 在 `cd://96` 主 hub。

---

## 开场 · Framing

"好, 这道题我把它 formulate 成一个 post 评论区的 top-3 选取问题——给定一个 viewer 和一个 post, 从这个 post 底下的评论池里, 选出 3 条排好序, 呈现在评论区顶部。

我先做几个假设, 确认一下边界。第一, user 这一侧, 我假设 viewer 是 primary user——他消费评论、决定要不要 engage; commenter 和 OP 是 secondary stakeholder, 我把他们折进 guardrail 里, 不单独建模。第二, 规模上, 我假设是亿级 DAU、大概 10% 的 commenting rate、viral post 峰值能到平均的 100 倍, 端到端 latency 我按 p99 200 毫秒来设计。

然后说 input、output 和 objective。这里我想先纠正一个我自己容易说顺嘴的地方——一个 post 底下的 comment pool 是 corpus, 它不是 model 的 input。一次 request 真正的 model input, 是 viewer feature、context feature, 加上候选 comment 的 feature 这三组。而且因为这个 pool 本身已经是 bounded 的, retrieval 这一阶几乎不存在——我会把它明确 formulate 成一个 ranking 加 set-selection 的问题, budget 全压在 ranker 和 reranker 上。

objective 上, user-end metric 要明确高于 biz metric。我的 north-star 是 weekly commenter return rate——一个数, 不是一串并行指标。它捕捉的是'看到了好的 top-3, 所以愿意去 engage, 所以长期会回来'这条链。guardrail 这一侧我要强调: 最重要的不是 revenue, 是 integrity——toxicity、harassment 这类 violation rate, 这是 UGC 评论区的大头; 再加 report rate 和 latency。

output 这一侧, 我们没有一个直接的 ground truth label, 所以要找 proxy。我会用 engagement 类的信号, 但负向信号这里特别脏, 因为有 selection bias, 具体怎么设计我留到 label section 展开。

最后说 twist——这道题和一个传统 recSys 不一样的地方, 我认为有三点, 每一点都带一个 design implication。第一, comment 不是一个 generic item——它是 ultra-short text, 而它的 authorship 是 social graph 上的一个节点, 所以主导信号是 relational 的, 不是 content-intrinsic 的。第二, early-comment time-bias——一个 post 生命早期发的评论会拿到不成比例的曝光, raw engagement count 把'到达时间'和'质量'这两件事 confound 在一起了。第三, community health 是 guardrail、不是 head——toxicity 是 disqualifying 的, 把 compliance 当成一个 soft loss term 是 category error。

整体方案: 一个 in-storage 的 pre-filter, 接一个两阶段的 point-wise ranking 漏斗 (L1 cheap、L2 deep), 最后一个 MMR 的 set-selection reranker。retrieval 因为 bounded 直接跳过。

这是我的 framing。接下来 metric、label、feature、model 这几块, 你想我先深入哪一块? 还是按顺序走?"

---

## Metrics

"好, metric 这一层我讲清楚, 后面 label schema 直接挂上来。

north-star 刚才说了, weekly commenter return rate, 因果链是'看到好 top-3 → 愿意 engage → 长期回来'。

往下我用 3 个 proxy, 每个挂一句 alignment: 第一, 评论区的 dwell time——top-3 有意思, 用户读得更久。第二, top-3 触发的 reply rate——top-3 能勾起对话。第三, 看完 top-3 之后用户自己发评论的 rate——top-3 激活了参与。

这里有一个 nuance 我想专门提——reply rate 这个 proxy 有一个 failure mode。rage comment、引战的评论同样能撬动大量 reply, 所以我不会单看 reply rate, 一定要配一个 sentiment 维度一起看。这其实是这道题最危险的那个 alarm, wrap 里还会再收一次。

因为 top-3 本质是 set selection, 我还需要一个 list-level metric——top-3 的 diversity score, 在 commenter、sentiment、topic 三个轴上算。

guardrail 这一侧讲三个就够: toxicity rate 卡硬阈值、每千次曝光的 report rate、p99 latency。fairness 相关的这里先不展开, 它和 integrity 走的是同一条 enforcement lane。

metric 大概这样。要不要我接着讲 label? label 是我觉得这道题最 non-trivial 的一块。"

---

## Labels

"好, label 这块。核心张力是 signal density 和 bias 之间的权衡——越显式的信号越准但越稀疏, 越 implicit 的越多但越脏。我分正向、负向两侧看。

正向用一个 label ladder。最 dumb 的版本是二元 engagement, 窗口内 like 或 reply。往上是 weighted multi-signal, reply > like > view-completion。我实际会选再上一层——engagement-to-impression ratio, 在一个 rolling 的 [T, T+1 小时] 窗口里算。它比 weighted 版本只多一步: 用 impression count 做 normalize。但这一步直接把'高位评论天然拿到更多曝光'这个优势除掉了, 等于把一部分 debias 前置到了 label 层, 比 model 层的 bias tower 早一道防线。

负向 label 是这道题真正的核心难点, 就是 selection bias。三阶来讲。第一阶, explicit negative——dislike、report, 强信号直接用。第二阶, exposed-not-engaged, 标准负样本, 但我不会原样用——我用一个独立的 logging-policy model 估出 propensity, 然后做 IPS-weighting, 低 propensity 的样本给更高的训练权重, 这是一个 counterfactual correction。第三阶, unexposed, 这是 naive 系统会崩的地方: 如果你把每一条没曝光过的评论都标成负样本, 你等于在教模型'凡是检索没捞到的好东西都是坏的'——这是 selection bias 最糟糕的表现形式。所以我把 unexposed 当成 unknown, 用一个 5% per-session 的 bandit exploration budget 去 backfill, 给 under-exposed 的长尾提供相对无偏的 label。

在这之上我还会从上一版模型挖一点 hard negative——高分但没 engagement 的, 教模型去 discriminate 那些'自信的错误'。batch 配比大概是 1 正样本配 3-5 个 IPS-weighted exposed-not-engaged、1-2 个 bandit 来的 unexposed、再加 0.5-1 个 hard negative, 具体数字用 ablation 调, 不写死。

最后一句 leakage guard: feature 的 snapshot 在 T 时刻取, label 在 [T, T+ΔT] 观测, 两个窗口不重叠。

label 我想讲到这。要不要我接着讲 feature? feature 里有一块我想多挖一层。"

---

## Features

"feature 我按 user、item、context、interaction 四个象限分, interaction 那一象限多讲一点——那是 twist 1 ('comment 不是 generic item') 真正兑现的地方。

user (viewer) 这一侧: demographic + topic-preference embedding、viewer 历史评论 engagement rate、viewer 的 sentiment 偏好。

item (comment + commenter sub-entity): comment 的 text embedding, 在评论创建时算一次; early engagement velocity, 注意是 rate 不是 count——time-debiased 的信号, 呼应 framing 里的 time-bias twist; commenter identity——verified / OP / viewer 有没有 follow。

context 比较直接: post topic 和 age、time of day、device。

interaction 这象限有两个结构性后果。generic item (视频、商品) 是 content object, signal 在内容本身; comment 是 ultra-short text, 可能就一句'lol'或一个 emoji, 文本 low-signal, predictive 的是'谁说的'和'viewer 跟 commenter 什么关系'。

第一, commenter 必须是 sub-entity, 有自己的 embedding。同一个 commenter 跨很多 post 出现, 可以学一个 shared representation——一个到处写出高 engagement 评论的人, 这个身份本身就是信号; 顺带还给 abuse 那一侧一个 reputation 抓手。

第二, 也是更重要的——这正是 retrieval 在这道题里只能是 ranking、不能是 two-tower 的结构性原因。最 predictive 的一组 feature 是 viewer × commenter 的 interaction term: follow 关系、viewer 历史上跟这个 commenter 的 engagement、viewer 自己评论历史和这条评论的语义相似度。这些都是 per-(viewer, comment) pair 的 cross feature, serving 时每个候选现算。two-tower 的 dot product 结构上就表达不了这种 pair-level interaction。所以我说的不是'ranker 比 two-tower 好一点', 而是'two-tower 结构上做不了这件事'。

feature 大概这样, 要不要我进 model?"

---

## Model

"model 分 pre-filter、两阶段 ranking、reranking 来讲, 最后用一小段收一下冷启动。

最前面是 pre-filter, 在 storage 本地做 toxicity 的 hard filter 加去重, 把候选砍到一千量级。我想在这里点一下 twist 3: toxicity 是一个 hard filter, 放在 ranker 之前, 它不是 ranker 里的一个 head, 更不是 loss 里的一个软项。把 compliance 当成一个 soft loss term, 是我觉得推荐团队经常犯的一个 category error——违规内容不是'engagement 少一点', 它是 disqualifying 的。

两阶段 ranking, L1 和 L2 不是两个无关的模型, 它们是同一个建模思路上的成本梯度。L1 是 cheap pre-rank, 把一千个候选快速砍到一两百, 只要别误杀 L2 本来会高分的就行。L2 才放开, 做 deep rank, 输出 point-wise 分数。

L2 做成 multi-task: shared bottom 加多个 head——engagement、一个 toxicity 的 monitor head、还有 diversity-contrib。我不会 day-1 就上 MMOE, 从 shared bottom 起步, 只有观测到 negative transfer 才升级。loss 权重用 business context 来锁——comment lift value 加 risk budget——不用 uncertainty weighting。原因: 这些权重是一个 product decision, 不是一个 statistical estimate, uncertainty weighting 解的是统计上的不匹配, 不是产品优先级。

L2 里我会专门加一个 shallow 的 additive bias tower。input 只有 bias feature——position、popularity、recency。training 时它的输出加到 main tower 的 logit 上, inference 时这个 bias 项整个置 0。为什么单独一个 tower、而不是把 position 塞进 main tower: shallow 的 inductive bias 吸收不了 content signal, 它只能留给 additive bias, 这样就逼着 main tower 学真正的 relevance; 而 position 混进 main tower 会造成 content 和 position 的 entanglement、inference 时的分布漂移、以及 position 偷走本该属于真实 feature 的 gradient。配套 training 时做 position-feature dropout, 让模型对 position 缺失更鲁棒。

reranking 我选 MMR、不选 DPP, 这是我觉得这道题最重要的一个架构 trade-off。n=3 时 list 太短了, DPP 那种 set-level 优化发挥不出来——三个 item 的 determinant 会被任意一对 pairwise cosine 主导, DPP 的理论优势 land 不下来。所以我用 MMR, 在 commenter、sentiment、topic 三个轴做, 再加一个 hard quota, 比如不能有两条同一个 commenter、最多一条 OP 自己的回复。我会明确说: 这不是'MMR 更好', 而是'MMR 适配 n=3 这个 regime, 如果 list 扩到 top-10 以上, 我就切 DPP 加 learned kernel'。

最后用一小段收冷启动。item 冷启动: 新评论靠创建时就算好的 text + social embedding 进 ranker, 这个 twist 1 已经给了, 所以新评论不会没有内容表征; engagement 统计量缺失时, 直接 fallback 到一个 default value。这里有个 nuance——这一点和 Reels 那种 feed 推荐不一样。Reels 那种场景 site-average fallback 不好, 是因为它跨整个 corpus 检索, 新内容要和全站比, 糊的 prior 会系统性 mis-rank。但 Top-3 永远只在一个 post 内部排序, comparison set 小而且 bounded, 一个 default value 不会造成系统性 mis-rank, 因为所有评论都在同一个 post 的 context 里互相比。所以这里不去搞复杂的 prior。唯一的 caveat: 如果哪天要做'跨 post 串流热评'的 surface, 这个假设才需要重新审视。user 冷启动保持轻量, onboarding 时让新用户过一个 diverse 的内容集, 拿早期 engagement 当相对无偏的偏好信号。

model 我想讲到这, 要不要我进 evaluation?"

---

## Evaluation & Monitoring

"evaluation 分 offline、online、long-term 三层, 然后讲 monitoring。

offline, 先看 per-head metric——engagement-to-impression 这个回归 head 看 weighted NDCG, binary head 看 AUC, 所有 metric 按 post age 和 commenter segment 切片。train/eval split 用 time-based 为主——comment ranking 对 freshness 敏感, random split 会泄漏 future popularity trend, AUC 被 inflate; 配一个 user-level holdout 抓'模型在记具体用户而不是学偏好'。

online A/B 有个这道题特有的陷阱——实验单位必须是 user 或 session 级, 不能是 item 或 impression 级。因为这是 set selection, top-3 里的 item 互相影响, impression 级随机化会污染。看的指标也要是 list-level: top-3 的 any-engagement rate, 不是单 item 的 NDCG / MRR。

monitoring 看四个信号, 按 leading 到 lagging 排序。第一, online 和 offline 的 metric gap——eval AUC 和线上 CTR 背离, 是 label leak 或分布漂移的早期信号。第二, prediction distribution shift, 模型输出分布的 day-over-day KL, 比 metric 退化更早, 是最 leading 的指标——大多数人只会说'monitor AUC', 这一个是 senior 信号。第三, feature drift, top feature 的 PSI, 小时级。第四, engagement metric 的 24 小时移动平均, 是 lagging 的——等它掉的时候用户已经走了。

第三层 long-term holdout, 4 周以上, 抓 filter bubble 收窄、fatigue 累积、creator 生态效应。north-star 是 weekly return, 没法每次 launch 等 4 周, A/B 决策接受 proxy-based, 但保留 holdout 做回溯校验。abuse detection 用独立模型, weekly retrain——adversarial drift 速度和 ranker drift 不是一回事。

evaluation 大概这样, 要不要我讲 serving?"

---

## Serving / Logging

"serving 和 logging, 我知道这不是 ML system design 考察的最大重点, 所以我给你几个我最在意的点, 不展开。

我最关心的是 train-serving skew。首选根治方案是 serving-time 的 shadow feature logging——serving 当下把喂给模型的 feature 值原样落盘, 训练直接用这一份, 不重新计算。

engagement velocity 这个 feature 必须是 streaming 的, 1-5 分钟 cadence。否则 framing 里我承诺的 time-bias mitigation 根本跑不起来——这是一条从 framing 的 product promise 到 serving infra cost 的 accountability chain, 我希望它显式。

latency 上, p99 200 毫秒, 候选规模一千量级, 关键设计是 feature prefetch 在 candidate retrieve 阶段就并行把 RPC 发出去, 等到 ranker 的时候 feature 已经在内存里。

cache: hot post 在 session 起始就把结果 cache 住, 5 分钟 TTL, 再加一个'有新的高 engagement 评论时主动失效'的机制。在 100 倍 viral 峰值下, cache 是 latency 的生命线。

production scar: 我们第一次上 shadow logging 时没用 async queue, inline 的写直接把 serving p99 顶高了 30%, 后来改成 fire-and-forget 的 pub-sub 才解决。

serving 我想讲到这, 要不要我 wrap 一下?"

---

## Wrap

"好, 我 zoom out 总结一下, 然后说三个我最担心的 risk。

整体是两阶段 point-wise ranking 加 MMR set-selection rerank。comment 用 relational representation (commenter 作为 sub-entity、viewer × commenter interaction term); position bias 靠 shallow bias tower 加 mask-at-inference; selection bias 靠 IPS 加 5% bandit exploration; evaluation 覆盖 offline、online、long-term 三层。

三个 risk。第一, selection bias 复利可能快过我们 mitigation, 5% 的 bandit 预算不一定够——我会监控 served diversity, 跌破阈值要有 circuit breaker。第二, multi-task 的 loss 权重会随数据分布漂移, retrain pipeline 要能重新调 head 权重, 不是固定组合下重训。第三, 也是最重要的——reply rate、engagement 涨, 但 commenter return 跌, 这就是 rage comment、引战内容在 gaming 我们的 proxy, 正好呼应 metric 段提的那个 nuance。这个最重要的 alarm, 靠 4 周的 long-term holdout 来抓。

这些就是我的设计, 有哪一块你想让我再深入吗?"
"""


FORMULAS = """\
# Label Ladder + Negative Sampling Ratio + Train/Eval Split 双轴 + Multi-task Conflict

## Positive label ladder (L1 -> L4, I pick L3)

| Level | Label                                                              | Trade-off / Why                                  |
|-------|--------------------------------------------------------------------|--------------------------------------------------|
| L1 (dumbest) | binary engagement (like / reply within window)              | sparse + position-biased                         |
| L2     | weighted multi-signal (reply > like > view-completion)             | engineering easy, but position bias remains      |
| **L3 (pick)** | **engagement-to-impression ratio in rolling [T, T+1h] window** | partial-debias position bias, time-aware         |
| L4 (follow-up) | multi-task labels with weighted heads                          | senior follow-up; topic is head-weighting design |

**Pick justification**: L3 adds one step over L2 -- **rolling-window normalize by impression count**. That step directly divides out the impression advantage a high-position comment gets, **front-loading partial debias to the label layer**, one defensive layer ahead of the model-level bias tower.

## Negative sampling batch composition

```
1   positive (exposed + engaged)
: 3-5 exposed-not-engaged (IPS-weighted)
: 1-2 unexposed (from bandit exploration data)
: 0.5-1 hard negative (mined from previous model -- high score but no engage)
```

**Three key design decisions**:

1. **IPS-weighted exposed-not-engaged**: propensity = P(item exposed | user, context) from a separate logging-policy model; low-propensity items get higher not-engaged sample weight (counterfactual correction).
2. **Bandit exploration backfill for unexposed**: 5% per-session impression budget for controlled exploration -> these impressions enter the training set providing unbiased label on the under-exposed long tail.
3. **Hard negative mining from previous model**: items with high prediction but no engagement -> teach the model to discriminate confidence-high mistakes.

**Why not 'unexposed = negative'**: introduces massive false negatives -- a good comment that simply wasn't retrieved gets a 0 label, teaching the model 'good things are bad' -- the worst manifestation of selection bias.

## Train/eval split (two axes)

**Primary axis -- time-based**:

- Train: `[T - 30 days, T - 1 day]`
- Eval: `[T - 1 day, T]`
- **Why time-based not random**: comment ranking is **freshness-sensitive** -- random split leaks future popularity trend (a viral comment already spikes inside the train period, so its future popularity is known to the train set -> AUC is inflated).

**Secondary axis -- user-level holdout**:

- 5% user holdout per time window, tests user generalization
- This axis catches "model memorizes specific users instead of learning preferences"

**Feature snapshot**: aligned to train/eval time, **daily snapshot strategy** -- every day all feature values are dumped, train consumes the snapshot for that day, **point-in-time correct, no future leakage**.

## Multi-task conflict (engagement vs toxicity) -- 3-option compare

| Option                                       | Mechanism                                                                  | Why pick / not pick                                              |
|----------------------------------------------|----------------------------------------------------------------------------|------------------------------------------------------------------|
| **Pick: Hard constraint via pre-filter + soft penalty in engagement head** | Toxicity > threshold -> pre-filter removes; remaining candidates: main head BCE + weak toxicity penalty term | Easy audit, clear failure mode, E4 boundary answer |
| Gradient surgery (PCGrad / GradVac)          | Project conflicting gradients orthogonal to each other                     | **Complexity not worth it** -- top-3 ranking is not GradNorm-class high-competitive multi-task |
| Reward shaping into single label             | `score = engagement - lambda * toxicity` composite label                   | **Loses eval diagnostic power** -- a single trained label cannot decompose attribution; the monitor head is also gone |

**Pick justification**: pre-filter (hard constraint) handles disqualifying violation + soft penalty (engagement head) handles borderline cases + monitor head (does not participate in loss) provides diagnostic -- three layers of clear responsibility, audit-able. E4 face level does not need PCGrad.

## Score combination (post-train tunable)

```
final_score = w_1 * p_engagement + w_2 * p_diversity_contrib + (- w_3 * p_toxicity)
```

Weights `w_k` **post-train tunable** -- engagement-vs-quality trade-off A/Bs can ship without retrain. Using `(1 - p_toxicity)` form (high score = unlikely toxic) is mathematically equivalent and matches the Reels golden convention.
"""


CHEAT_SHEET = """\
# 30-sec pre-walk-in checklist -- Top-3-Comments-only

Methodology (timing skeleton, 元结构, 8 meta-rules, E4/E5 boundary, drift-recovery vocab) lives in `cd://96` §1 / §5 / §6 / §8. The anchors below are Top-3-Comments-specific only -- quote verbatim, do NOT overlap cd96.

## Strong Moment slot map (memorize position, anchor, twist)

| Time   | Slot    | Top-3-Comments-specific anchor (the twist this slot hosts)                         |
|--------|---------|------------------------------------------------------------------------------------|
| 0-1    | **#1**  | 3 unique twists -- comment != item / time-bias / community-health-as-guardrail     |
| 8-12   | **#2**  | Selection bias 3-stage negative label -- IPS + 5% bandit + hard-neg mining         |
| 15-21  | **#3**  | Bias Tower + MMR vs DPP -- additive separable + mask-at-inference + 3-axis quota   |
| 31-35  | **#4**  | 4 monitoring signals -- prediction distribution shift earlier than engagement       |

## Top-3-Comments-only quantification anchors (drop verbatim into the appropriate moment)

- **15 / 25 min split**: 前段 framing/metric/label/feature, 后段 model/serving/monitoring -- the Top-3 time plan declared in the first 60s.
- **5% per session**: bandit exploration impression budget -- the selection-bias twist of Strong Moment #2.
- **3-axis MMR**: commenter / sentiment / topic + hard quota (no 2 same commenter, <=1 OP self-reply) -- the architecture twist of Strong Moment #3.
- **n=3 vs n=10+**: MMR is the regime answer for n=3; DPP switches in at n=10+ -- the unique angle.
- **5-min TTL cache + high-engagement invalidation**: the 100x viral-peak production lever.
- **200 ms p99** over **~1000 candidates** with **60/10/80/30/20 ms** stage budget; engagement velocity at **1-5 min streaming** cadence -- the scale anchors for the serving and feature sections.
- **4-week long-horizon holdout** for north-star (weekly commenter return); A/B ramp accepts proxy-based decisions.

## Top-3-Comments-only firm-claim register (each line is said at most once during the 45 min)

- "**This is a set-selection problem, not pure ranking.**"  (Twist framing callback)
- "**It is a stronger lever than IPS, but it requires cross-functional cost** -- product and growth pay part of the bill."  (Selection-bias twist callback)
- "**For n=3, MMR with hard quota gives me a deterministic diversity guarantee with auditable knobs; DPP at n=3 is solving for n=20 with n=3 evidence.**"  (Architecture twist callback)
- "**Treating compliance as a soft loss term is a category error.**"  (bonus, said once after #3)
- "**Prediction distribution shift is earlier than metric degradation -- the leading-est indicator.**"  (Monitoring twist callback)

## Reuse range (one-line note, full mapping in cd://96)

This row's 2-stage point-wise + MMR list-level + bias tower + 4-quadrant features + 4 monitoring signals + independent abuse model + tiered refresh + shadow logging shape is the canonical **list-level / set-selection** carve-up. For Reels / Notification / Friend-rec / Ads mappings see the cd://96 hub and the sibling sd-golden rows (`sd://meta-reels-golden`, `sd://meta-weapon-ads-golden` planned, `sd://meta-friend-rec-golden` planned).

---

## Design Doc 强调话术 (verbatim user reference §8, 4 closing sentences)

**For interview / Design Doc / Code Review settings, say these 4 lines verbatim**:

1. **「采用加性 shallow bias tower，结构性强制 relevance / bias 分解」**
2. **「Mask-at-inference 提供干净的反事实排序信号」**
3. **「Shadow feature logging 保证 bias 特征训练/服务分布一致，避免 debias 机制被 skew 破坏」**
4. **「离线 AUC 可能持平甚至微跌，业务指标 (多样性 / 留存 / 新内容曝光) 为真实评估目标」**

Why these 4 sentences are the killer ending:

- Sentence 1 = architectural commitment (additive structure + capacity bottleneck as inductive bias)
- Sentence 2 = inference correctness (counterfactual semantics, not an engineering hack)
- Sentence 3 = data-layer accountability (skew defense is a prerequisite, not nice-to-have)
- Sentence 4 = **business-metric alignment** -- "ship with offline AUC flat or slightly down" is the E5 boundary signal: you know the relationship between ML metric and product metric and refuse to be bound by offline numbers.
"""

# T-P1-881: oral_narrative archetype NULLs these 5 fields. Their content lives
# inlined in DATAFLOW (the 8-section 口播稿); verbal_outline is re-populated by
# seed_meta_meta_top3_comments_golden_verbal_outline.py (run AFTER this seed).
# Validation in scripts/audit_meta_mlsd_3rule.py respects the archetype declared
# on the instance in schemas/meta_mlsd_canonical.yaml.
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
    """Archetype-aware seed-side validation (oral_narrative).

    Verifies the 4 contracted fields populated above their floor, the 5 NULL
    fields actually NULL (verbal_outline is NULL at this point -- the verbal seed
    runs AFTER), content_hash present, and slug/subtitle/display_order. Deep
    semantic checks (R-3RULE-* / R-NARRATIVE-* / R-CHAR-range / R-DRAWER-no-sd-
    drawer) live in scripts/audit_meta_mlsd_3rule.py and are the canonical gate.
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

    # NULL-fields contract for oral_narrative (verbal_outline re-populated later).
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
