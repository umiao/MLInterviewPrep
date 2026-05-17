"""Seed: T-P0-870 [Meta-MLSD] Friend Recommendation Golden -> system_designs.

INSERTs (or idempotently updates) the canonical Meta MLSD Friend Recommendation
golden example as ``system_designs(slug='meta-friend-rec-golden')``,
drawer-reachable via ``sd://meta-friend-rec-golden``. This is a **bilateral
matching** golden -- sibling of ``sd://meta-reels-golden`` (RecSys),
``sd://meta-top3-comments-golden`` (list-level), and
``sd://meta-weapon-ads-golden`` (T&S classification). Cross-link via cd://96
§1/§3 drawers (added by T-P0-871).

T-P0-895 archetype migration (2026-05-16): document_archetype migrated from
``structured_reference`` (10-field shape, ~50KB across overview/architecture/
dataflow/formulas/production_constraints/tradeoffs/defense/verbal_outline/
cheat_sheet) to ``oral_narrative``, mirroring the sd41 golden template
established by T-P1-875 + T-P0-892 and the sd43 mirror by T-P0-894. Per the
archetype's contract in ``schemas/meta_mlsd_canonical.yaml``
(``document_archetypes.values.oral_narrative``):

  - ``dataflow`` carries a single continuous 第一人称 45-min 口播稿 (8 sections:
    开场 Framing / Data & Label / Features / Model / 冷启动 / Evaluation /
    Serving / Wrap).
  - ``overview`` / ``formulas`` / ``cheat_sheet`` are slim anchors.
  - ``architecture`` / ``production_constraints`` / ``tradeoffs`` / ``defense``
    / ``verbal_outline`` are NULL by design -- their content lives inlined in
    the dataflow narrative (立场 + trade-off + Strong Moment + verbatim).
    ``verbal_outline`` is populated separately and authoritatively by
    ``scripts/seed_meta_friend_rec_golden_verbal_outline.py`` (T-P0-895 part B),
    a verbal-only seed that opts this oral_narrative row INTO a speaking
    skeleton for the SystemDesignDrawer (which renders verbal_outline first
    since T-P0-891). This main seed NULLs it; run the verbal seed last.

Rationale: the structured_reference shape spread the same Friend-Rec insights
(graph-native bilateral matching / network-effect counterfactual / NRT
bilateral signal / abuse-posture upstream) across overview -> architecture ->
dataflow -> defense, each restating the others, and tripped R-CHAR-range +
R-NARRATIVE-bold-density on the 10.5KB dataflow. The oral_narrative shape
consolidates everything into one continuous oral-recital script; the audit
(scripts/audit_meta_mlsd_3rule.py) skips R-CHAR-range / R-NARRATIVE / the
nullable fields for oral_narrative and only enforces dataflow >= 4000 chars +
the section-level 3-rule.

The diff-delta baseline for this oral_narrative instance is recorded on the
``meta_mlsd_canonical.yaml`` instance as ``baseline_chars_post_migration:
10576`` (the structured_reference dataflow size at migration time -- the new
floor against which future deletions are gated; the migration commit itself is
exempt).

A pre-migration safety backup exists at
``data/backups/mle_prep_pre_friend_komantxe_20260514_114845.db`` (revert path
if the oral_narrative content is rejected on review).

Idempotent: re-running upserts in place by ``slug``. Sentinel-based UPSERT
keyed on ``slug='meta-friend-rec-golden'``. Two consecutive runs leave the DB
byte-identical (the row payload is fully deterministic).

Usage::

    python scripts/seed_meta_friend_rec_golden_sd.py [--db data/mle_prep.db] [--dry-run]
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

SLUG = "meta-friend-rec-golden"
TITLE = (
    "Meta MLSD Golden Example: Friend Recommendation "
    "(Bilateral matching, 45min walkthrough)"
)
SUBTITLE = (
    "Meta MLSD Golden Example — 第一人称完整 45min 口播稿 "
    "(因果链 + 立场+trade-off + twist 在 body 兑现 三原则). "
    "Bilateral matching 题型 (graph-native, P(send) x P(accept), NOT 单 ranker); "
    "4-twist framing (graph-native bilateral matching / network-effect "
    "counterfactual / NRT bilateral signal / abuse-posture upstream). "
    "方法论 (Strong Moment 调度, ML-native vocab, 8 meta-rules, E4/E5) 在 cd://96。"
)
DISPLAY_ORDER = 133
SOURCE_PATH = (
    "docs/prep/meta_mlsd_2026-05-13_friend_rec/"
    "source_07_friend_recommendation_rewritten.md"
)

ANCHOR_FR_NODE = "meta-prep/system-design-must-knows/mmoe-ple-multitask"

# T-P0-895: this seed produces an oral_narrative archetype document. See
# schemas/meta_mlsd_canonical.yaml > document_archetypes.values.oral_narrative.
DOCUMENT_ARCHETYPE = "oral_narrative"


OVERVIEW = """\
# Friend Recommendation — 45min Golden 口播稿

按"因果链 + 立场+trade-off + twist 在 body 兑现" 三原则写成的完整第一人称口播稿。完整 8 段台词在 `dataflow` tab; bilateral matching score / MMoE multi-head gating / cluster-randomized A/B 三个公式 anchor 在 `formulas`; 数字 anchor + firm-claim register + Design Doc 强调话术在 `cheat_sheet`。方法论 (timing skeleton, Strong Moment 调度, ML-native vocab YES/NO, 8 meta-rules, E4/E5 boundary) 在 `cd://96` 主 hub, 此 row 只承载 Friend Recommendation 这一题的 solution。

这道题我一上来就 reframe: 它不是一个 single P(click) ranker, 它本质是一个长在 social graph 上的 **bilateral matching** 问题——optimization target 是 `P(send) x P(accept)`, 一个由两个非对称分布相乘出来的量, 不是单边的 click。四条 driving twist 在 framing 段就 declarative 立起来, 后续每个 component 兑现:

1. **Graph-native bilateral matching** (压舱石 signature) — 整题活在一张秒级 mutate 的 friend graph 上; 这个 graph-native 性质同时解释了为什么 target 是两个非对称分布的乘积、为什么 user-level A/B 会被 edge 污染、为什么 recent state 在 score time 才有意义。落地: MMoE multi-head bilateral, shared bottom + 两个 gating head (一个 route 到 P(send) tower, 一个到 P(accept) tower), serving score 是 product, per-relationship-type calibrated。
2. **Network-effect counterfactual** — treatment effect 沿 friend edge 泄漏, user-level 随机化两臂互相污染。落地: cluster-randomized A/B 在 Louvain / Leiden community 上做, leave-one-cluster-out 方差恢复 + SUTVA-violation 诊断进实验契约。
3. **NRT bilateral signal** — friend graph 秒级变化, 双方 recent state 都在 score time 才有信息量, daily snapshot 漏掉 90%+ 的 recent-action surface。落地: Kafka -> Flink 双侧 streaming join, last-N 秒 accept/reject/block 在 score time join 进模型, 60s 端到端 SLA。
4. **Abuse-posture is upstream** — spammer 把 P(send) 拉满、abuse-victim 把 P(accept-from-stranger) 压到底, abuse 过滤必须在 retrieval 之前。落地: abuse-aware admission gate 在 retrieval 前 + per-relationship-type calibration 让 growth threshold 与 safety threshold 在同一概率刻度上 compose。

整体方案: abuse-aware admission gate → 5-channel retrieval funnel (mutual / 2-hop / two-tower embedding / cohort / inferred-real-life) → MMoE multi-head bilateral ranker, NRT bilateral signal 在 score time join, serving score = `P(send) x P(accept)` per-relationship-type calibrated。"""


DATAFLOW = """\
# 完整 45min 口播稿 (第一人称, 8 段连续)

> Section 标题只是导航用, 真讲的时候是连续说下来的。每段串因果链, 每立场挂 trade-off, framing 立的四个 twist (graph-native bilateral matching / network-effect counterfactual / NRT bilateral signal / abuse-posture upstream) 在 body 里逐一兑现。

---

## 开场 · Framing

"好, 这道 Friend Recommendation 的题, 我开口第一件事是 reframe: 我不会把它做成一个'预测你会不会点这个人'的 single P(click) ranker, 我把它 formulate 成一个长在 social graph 上的 **bilateral matching** 问题——真正要优化的是 `P(send) x P(accept)`, 一个由 sender intent 和 receiver receptivity 两个物理上非对称的分布相乘出来的量。这个 reframe 本身就是这题的 senior signal, 因为只优化 sender 一侧会把 receiver 淹在垃圾请求里, 平台价值反而塌掉。

我先 confirm 几个边界。规模上, 我假设几亿 DAU、几十亿条 friend-graph edge、每天几千万次 people-you-may-know 曝光; 一次 request 经 retrieval 后候选池 ~10k, top-K=20。SLA 上, 端到端 p99 < 100 ms (home-feed PYMK unit), retrieval 5 路并行 p99 < 30 ms, ranker p99 < 50 ms, NRT 双侧 lookup p99 < 10 ms, NRT freshness < 60s, abuse-flag 每 6 小时刷新。input 是 (requesting user A, candidate B, interaction-pair) 三组 feature, friend graph 是 corpus 不是 model input。

然后是这题和一道普通 recommendation 不一样的地方, 我认为有四个 twist, 我现在就 declarative 立起来, body 里逐个兑现。第一, 也是整场压舱石——**这是 graph-native 的 bilateral matching**, 整题活在一张秒级 mutate 的 social graph 上, 这个 graph-native 性质同时派生出后面三个 twist。第二, **network-effect counterfactual**——treatment 沿 friend edge 泄漏, user-level A/B 两臂互污。第三, **NRT bilateral signal**——双方 recent state 只在 score time 有信息量。第四, **abuse-posture is upstream**——abuse 过滤必须在 ranking 之前, 不是事后 rerank。

整体方案我先给一句: abuse-aware admission gate 守在 retrieval 前面, 5 路 retrieval funnel 各召一种 friend-type 信号, MMoE multi-head bilateral ranker 出 calibrated `P(send)` 和 `P(accept)`, 两者相乘当 serving score, NRT 双侧信号 score time join。这是我的 framing, 你想我先深入 label, 还是 model 和 serving?"

---

## Data & Label

"我从 label 开始, 因为这题最 non-trivial 的就是'什么算一个正样本'本身就是个 senior judgment, 不是 model。

**我选 bilateral positive: send AND accept AND 28 天内 >= 1 次 post-acceptance interaction**。为什么不是 send-only? send-only 会被 spammer 把 P(send) 拉满直接刷爆; accept-only 又会被勉强接受、接受完零互动的 reluctant accept 钻空子。28 天 sustained engagement (接受后双方的 message / post / reaction 数) 才是和平台价值对齐的信号。**代价是**一个 28 天的 label 成熟延迟, 我用 eligible-label fast-track 缓解——已经跨过 send AND accept 的近期 item 当 provisional positive, 但 sample-weight 下调。

negative sampling 我特意做**非对称**: P(send) head 用 70/30 random/hard split, 因为 sender 边界宽、broad random negative 维持 retrieval recall; P(accept) head 用 50/50 split, 因为 receiver 决策更难、需要 impressed-but-not-clicked 的 hard negative 才学得到接收侧的边界。一个统一采样率会逼出一个两个 head 都欠拟合的折中。

eval 这块我有一个不能 collapse 的纪律——**三套 eval set, 各回答不同问题**: frozen golden set 取 4 周前的切片、永不更新, 回答'有没有过固定的 bilateral-engagement bar'; rolling weekly set 每周一从上周成熟 label 刷新, 回答'这周流量上表现如何'; cluster-randomized counterfactual set 持续更新, 回答'cluster A/B 的反事实估计趋势是否一致'。把三套合成一套是常见错误——一个 model 在 frozen 上好看, 在 cluster counterfactual 上可能已经 silently 崩了。这里没有 bandit exploration, 因为一个错误 friend-rec 的代价是 abuse / 平台信任, 不是一次 UX 实验。"

---

## Features

"feature 我按 sender / receiver / interaction / context 四类拆, 但这题最重的象限是 interaction-side (sender x receiver pair) 的 relational, 这正是 graph-native twist 在 feature 层兑现的地方。

sender (user A): friend-graph degree + 最近 friend-add velocity (sender-intent), browse history + PYMK dwell + 最近 profile-view, 最近 send-reject ratio (压低长期 spammer)。

receiver (user B): friend-graph degree + accept-rate-from-strangers (receiver-receptivity), 最近 block / report 行为 (abuse-victim 信号), inbox depth (过载 receiver 不论 fit 都少接受)。

interaction (最重象限, bilateral twist 落地): **mutual-friend count + Adamic-Adar weight** (便宜的 graph 邻接 anchor), **channel-of-origin** 当 one-hot (mutual / 2-hop / embedding / cohort / inferred-real-life), cohort overlap depth (同校 / 同雇主 / 同 group), inferred-real-life (org chart / contact-book hash join / location co-presence)。

我想强调一个 critical distinction: **NRT lane 携带的是 state feature 不是聚合量**——双侧 last-N 秒的 accept/reject/block 事件, 在 score time join。这就是为什么一个 daily-batch-only 的 feature set 不够: 没有 NRT lane, 一个刚拒了三个请求的用户会在同一小时内被再推相似候选, 而那个'停'的信号 daily snapshot 永远看不到。这条 twist 我会在 model 段再兑现一次。"

---

## Model

"model 我做 5-channel retrieval funnel 接一个 MMoE multi-head bilateral ranker, 不做单一大 ranker。

**我选 MMoE multi-head 不选 single weighted-loss ranker**, 因为 sender-side 信号 (browse、mutual-friend count) 和 receiver-side 信号 (recent-block、accept-rate-from-strangers) 物理上非对称, 一个 single weighted loss 会逼出一个两个 head 都欠拟合的折中。结构: shared bottom 编码 user + candidate + interaction, 两个 gating head 各产出 expert 的 soft mixture 喂两个 task tower (P(send) / P(accept))。代价是两个 task head + per-task gating + 一张 joint calibration table; 只有当两个 head 之间出现 negative transfer 才 switch 到 PLE, 这个 corpus 规模上还没观察到。

serving score 是两个 head 的 **product** `P(send) x P(accept)`, 不是 sum——product 是一个 calibrated bilateral 概率而不只是 ranking, 这个性质让 growth threshold 和 safety threshold 在 policy 层能在同一刻度上 compose。每个 head per-relationship-type temperature scale (stranger / colleague / school / real-life-contact), 因为 base-rate acceptance 随 relationship type 从 ~5% 到 ~80% 漂, 一个全局 temperature 会 over-pull stranger 又 under-pull real-life-contact。

retrieval 5 路并行: mutual-friend (O(degree) graph 邻接), 2-hop (Counter-based hop-aggregation, 6 小时 cache), two-tower embedding (HNSW M=32 p99 < 8 ms), cohort overlap, inferred-real-life。每路出一个 per-channel-scored pool, union 去重并保留 **channel-of-origin 当 one-hot** 给 ranker fusion——5 路并行是一个 candidate-coverage decomposition (各 surface 一种 friend-type 信号), 单一 end-to-end retrieval 会把 5 种信号 conflate 进一个 loss 还丢掉 per-channel recall 的可调试性。model ladder 我一句话压缩: LR -> XGBoost -> DNN -> MMoE -> Transformer, 每步被前一步一个具体 failure 推动, MMoE 是 deployed default (offline AUC 比 Transformer 差 < 0.5% 但 p99 便宜 ~3x), Transformer 是 sequence-aware bilateral 的 next tense。"

---

## 冷启动 (承接 model)

"冷启动这题主要是 new-user cold-start 和 new-edge 稀疏, 不是 new-item。

一个全新或低度数用户, friend-graph degree 近零、interaction 历史空, naive 做法会退到 site 均值。**我的处理是**让 graph-native 信号兜底——即使账号是新的, 它的 contact-book hash join / org chart / 共同 group 往往不是新的, inferred-real-life channel + 2-hop graph 沿这些边传播过来的 prior 是冷启动期唯一相对无偏的信号。fallback 顺序我特意写清楚: 先 graph-propagated / inferred-real-life prior, 再 cohort (同校同雇主) base rate, 最后才是全局 prior, 不直接 fallback 到全局 (太糊)。

onboarding 期走一个轻量 diverse 候选集 + 略升 exploration 比例, 但仍过 abuse-aware admission gate, 因为'新用户'不等于'安全'——新号恰恰是 spammer 最爱的入口。bandit 我知道是选项, 但这里 explore 的代价是 abuse 暴露, 我点到为止, 不展开。"

---

## Evaluation

"evaluation 我分三层, 而且我会主动讲监控顺序, 因为这是 E5 的 boundary signal。

第一, **cluster-randomized A/B, 是这题的实际 change-management surface**。user-level 随机化会沿 friend edge 泄漏 treatment——我们踩过一次坑, 一个 user-level A/B 看着强正向, 在 cluster-randomization 下直接消失, leaked treatment 经被接受的请求污染了 control 臂, user-level 估计被高估了 ~40%。所以实验**必须**在 Louvain / Leiden community cluster 上随机化, 方差用 **leave-one-cluster-out** delta method 恢复 (cluster 大小不均, naive 标准误低估真实 CI 2-4x)。SUTVA-violation 诊断进实验契约: cluster 估计与 user-level 估计偏离 > 20% 就 reject user-level 结果只报 cluster。代价是每 cell ~10x sample size + 每周 clustering 刷新; 只有 post-acceptance outcome (网络已 mutate、SUTVA 不再违反) 才 switch 回 user-level。

第二, **三套 eval set 持续跑**: frozen golden 当固定 bar tracker, rolling weekly 周一刷新后读, cluster counterfactual 持续从 live 实验 cluster 更新。不要 collapse 成一个数, 每套 gate 一个不同的 production action (frozen gate calibration rotation, rolling gate ranker retrain release, cluster gate 实验 sign-off)。

第三, **online prediction-distribution drift, 每小时**, 对 P(send) 和 P(accept) 两个 head 各做 day-over-day KL divergence 抓 base-rate shift, 这比三套 eval set 还早。大多数候选只会说'monitor AUC', 这条是 senior signal。offline metric 按 relationship-type 和 sender/receiver segment 切, 因为 base rate 和代价结构都随 relationship type 变; calibration 每晚用 frozen golden 上 per-(task, relationship-type) ECE 查 drift, 任一 cell 破 2% 就 halt calibration rotation——circuit breaker, 不是人工 review。"

---

## Serving / Logging

"serving 和 logging 我给几个最在意的点, 不展开。

latency: retrieval 5 路并行 p99 < 30 ms (mutual O(degree) p99 < 10 ms / 2-hop 6h cache p99 < 15 ms / two-tower HNSW M=32 p99 < 8 ms / cohort p99 < 15 ms / inferred-real-life p99 < 20 ms), MMoE ranker 在去重后 ~10k 池上 p99 < 50 ms, NRT 双侧 hot-key lookup p99 < 10 ms, 端到端 p99 < 100 ms; onboarding 高峰 ~5x 平均。NRT bilateral signal 必须 score time join 不能 batch precompute, 因为 recent-action 秒级衰减、最有信息量是在 60s 内——没有它 ~90% 曝光的 recent-action 信号都漏掉, 这是 feature 段那个 graph-native twist 在 serving 层的最后一次兑现。

最关键的运维面我认为不是 model weight, 是 **cluster-randomized A/B 契约 + rollout circuit-breaker**。新 MMoE ranker 走 shadow + 1% **cluster** canary -> 5% -> 25% -> 100% (cluster-canary 不是 user-canary, 因为 user-canary 经 network spillover 污染 control 臂), 三个 guardrail 任一破自动 halt——P(send) head AUC 跌破 baseline-0.5%、P(accept) head AUC 跌破 baseline-0.5%、cluster-randomized 28 天 sustained-engagement 趋势跌破 baseline-1%。train-serving 一致性上, calibration temperature 离线在 validation set 上算、线上原样应用, 周期性用 online-served data 重算校对, 偏差 > 5% 冻结 calibration rotation。"

---

## Wrap

"我 zoom out 收一下, 然后说三个我最担心的 risk。

整体是一个长在 social graph 上的 bilateral matching: abuse-aware admission gate → 5-channel retrieval funnel → MMoE multi-head bilateral ranker, serving score = `P(send) x P(accept)` per-relationship-type calibrated, NRT 双侧信号 score time join, 实验走 cluster-randomized A/B + SUTVA 诊断, rollout 走 cluster-canary circuit-breaker。

三个 risk。第一, NRT lane 退化或 freshness 窗口设太宽, recent-action 信号在窗口内丢掉, 修法是 60s 端到端 SLA + freshness > 5min 软报警 + daily-batch 降级 fallback。第二, user-level A/B 的 network spillover 把效应高估 (我们踩过 ~40% 的坑), 修法是 cluster-randomized A/B + leave-one-cluster-out 方差 + SUTVA divergence > 20% 自动 reject user-level。第三, 也是最重要的——把 bilateral matching 当成一个 single weighted-loss task 做, 这是 category error, 会丢掉 product 的 calibrated-bilateral 性质, 修法是 MMoE multi-head + product serving score + per-relationship-type calibration, alarm 靠 negative-transfer monitor (per-task AUC 背离) 抓。

这些是我的设计, 哪一块你想让我再深入?"
"""


FORMULAS = """\
# 三个公式 anchor (口播稿对应的形式化, 面试官追问时打开)

> 口播稿原文在 `dataflow` tab; 此处只放 bilateral matching score / MMoE multi-head gating / cluster-randomized A/B 三个 anchor 的精确定义, 面试官追问公式时打开。

## Bilateral matching score (optimization target)

对候选 pair `(A, B)` (A 是请求用户, B 是被推候选), 模型出两个 calibrated score:

```
P(send   | A -> B) = sigmoid(z_send   / T_send[reltype(A,B)])
P(accept | A -> B) = sigmoid(z_accept / T_accept[reltype(A,B)])
score(A, B)        = P(send | A -> B) * P(accept | A -> B)
```

per-relationship-type temperature `T_send[reltype]` / `T_accept[reltype]` 对 `stranger / colleague / school / real-life-contact` 分别校准。没有 per-relationship 校准, 一个全局 temperature 会 over-pull stranger (base-rate accept ~5%) 又 under-pull real-life-contact (~80%)。product 是 calibrated bilateral 概率而非 ranking, 这是 growth / safety threshold 能在 policy 层 compose 的前提。

## MMoE multi-head gating (architectural anchor)

bottom 把 user + candidate + interaction 编成 shared 表征 `h` (维度 `d`)。对每个 task `t in {send, accept}`, softmax gate `g_t(h)` 产出 `n` 个 expert 的混合:

```
g_t(h)      = softmax(W_t * h)                # shape (n,)
mix_t(h)    = sum_{i=1..n} g_t(h)_i * E_i(h)  # shape (d',)
P(t | A,B)  = sigmoid(tower_t(mix_t(h)))      # task-specific scalar head
```

每个 expert `E_i` 是跨 task 共享的小 MLP; per-task gating 让两个 head 借力重叠 expert 而不强行硬分割。**negative-transfer monitor** 跟踪 per-task AUC drift: 若 `AUC_t1` 退化而 `AUC_t2` 提升, gate 在短接 t1, 触发 gate-regularization 或 PLE 迁移。

## Cluster-randomized A/B + leave-one-cluster-out 方差

SUTVA 违反下, user-level 随机化的 treatment effect 有偏。在 community level 上 cluster 随机化恢复无偏估计。`K` 个 cluster, 分配 `Z_k in {0,1}`, per-cluster 平均结果 `Y_k`:

```
TE_cluster = (sum_k Z_k Y_k)/(sum_k Z_k) - (sum_k (1-Z_k) Y_k)/(sum_k (1-Z_k))
var_LOCO   = (K/(K-1)) * sum_k (TE_{-k} - mean_k TE_{-k})^2
```

`TE_{-k}` 是留掉 cluster `k` 的 treatment-effect 估计。LOCO 方差恢复**代价是更多 cluster** (方差随 cluster 数而非 user 数缩放), 逼出比 user-level ~10x 的 sample size, 但在 network spillover 下恢复无偏反事实。SUTVA 诊断: cluster 估计与 user-level 偏离 > 20% 即 reject user-level。"""


CHEAT_SHEET = """\
# 30-sec pre-walk-in checklist — Friend-Rec-only

> 方法论 (timing skeleton, 元结构, 8 meta-rules, E4/E5 boundary, drift recovery vocab) 在 `cd://96` §1 / §5 / §6 / §8。此处只放 Friend-Rec 特有的 anchor 数 + firm-claim register + Design Doc 强调话术, 进面前 30 秒过一遍。

## 数字 anchor (说出来时声音里就有数)

- **几亿 DAU / 几十亿 friend-graph edge / 每天几千万 PYMK 曝光**: scale anchor
- **~10k 候选池 / top-K = 20**: retrieval -> rank 漏斗
- **端到端 p99 < 100 ms**: retrieval 5 路并行 < 30 ms / ranker < 50 ms / NRT 双侧 < 10 ms
- **NRT freshness < 60s, abuse-flag 6h 刷新, 2-hop 6h cache**: 双侧 streaming SLA + tiered cadence
- **HNSW M=32 p99 < 8 ms**: two-tower embedding channel recall@100 ~95%
- **daily ranker retrain / weekly two-tower + Louvain 刷新**: tiered cadence
- **bilateral positive = send AND accept AND >= 1 post-accept interaction @ 28 天**: 正样本定义
- **negative sampling 70/30 (P(send)) vs 50/50 (P(accept))**: 非对称采样
- **base-rate accept ~5% (stranger) .. ~80% (real-life-contact)**: per-relationship calibration 必要性
- **user-level A/B 高估 ~40% / SUTVA divergence > 20% reject / LOCO ~10x sample size**: network-effect counterfactual anchor
- **rollout shadow + 1/5/25/100% cluster canary + 3 guardrail (P(send)-AUC / P(accept)-AUC / 28d-engagement)**: change-management lane
- **ECE <= 2% per (task, relationship-type)**: calibration circuit-breaker 阈

## Firm-claim register (整场至多说 1 次)

- "**这不是 single P(click) ranker, 是长在 social graph 上的 bilateral matching**——target 是 `P(send) x P(accept)`, 两个非对称分布的乘积。" (开场 reframe 立场)
- "**graph-native 性质同时派生出后三个 twist**——network counterfactual / NRT signal / abuse posture 都是因为整题活在一张秒级 mutate 的 graph 上。" (Twist 1 压舱石 callback)
- "**user-level A/B 沿 friend edge 泄漏 treatment, 我们踩过 ~40% 高估的坑——cluster-randomized 是实际 change-management surface。**" (Twist 2 callback)
- "**NRT bilateral signal 是 score-time state feature 不是 batch 聚合——daily snapshot 漏 90%+ recent-action。**" (Twist 3 callback)
- "**abuse-posture 在 retrieval 之前, 不是事后 rerank——spammer recs 绝不能进候选池。**" (Twist 4 callback)
- "**product 是 calibrated bilateral 概率不是 ranking——这是 growth / safety threshold 能 compose 的前提。**" (Model 立场)

## 复用范围

此 row 的 graph-native bilateral matching + MMoE multi-head P(send)xP(accept) + 5-channel retrieval funnel + NRT 双侧 score-time signal + cluster-randomized A/B + abuse-aware admission gate 是 **bilateral matching** 这一题的 carve-up。RecSys / list-level / T&S-classification 等其他 Meta MLSD 题型的 mapping 见 `cd://96` 主 hub (不在此 row 内 bundle sibling)。

---

## Design Doc 强调话术 (interview / Design Doc / Code Review 通用的收尾句)

**这 4 句 verbatim 说出来**:

1. **「Friend-rec 是长在 social graph 上的 bilateral matching：optimization target 是 `P(send) x P(accept)`，由两个物理非对称分布相乘，不是 single P(click) ranker。」**
2. **「MMoE multi-head：shared bottom + 两个 gating head 喂 P(send) / P(accept) 双 tower，serving score 取 product 并 per-relationship-type calibrated，growth 与 safety threshold 在同一刻度 compose。」**
3. **「实验必须 cluster-randomized A/B（Louvain/Leiden）：user-level 沿 friend edge 泄漏 treatment，曾高估 ~40%；leave-one-cluster-out 方差 + SUTVA divergence > 20% reject user-level。」**
4. **「NRT bilateral signal 是 score-time state feature（双侧 last-N 秒 accept/reject/block，60s SLA）；abuse-aware admission gate 在 retrieval 之前，不与 model weights 共用 release cadence。」**

四句分别是: 问题 formulation (graph-native bilateral matching)、架构承诺 (MMoE multi-head + product + per-relationship calibration)、实验纪律承诺 (cluster-randomized A/B + SUTVA 诊断)、production-process 承诺 (NRT score-time + abuse gate 独立 lane) ——这是 E5 boundary signal: 你懂 ML metric / network-effect counterfactual / abuse posture 三者关系, 拒绝把它们 collapse 成一个 single ranker。"""


# T-P0-895: oral_narrative archetype NULLs these 5 fields. Their content lives
# inlined in DATAFLOW (the 8-section 口播稿). verbal_outline is populated
# separately and authoritatively by
# scripts/seed_meta_friend_rec_golden_verbal_outline.py (run it last).
# Validation in scripts/audit_meta_mlsd_3rule.py respects the archetype
# declared on the instance in schemas/meta_mlsd_canonical.yaml.
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
    """Archetype-aware seed-side validation (mirrors sd41/sd43's oral_narrative gate).

    For oral_narrative: verify the 4 contracted fields populated above their
    floor, the 5 NULL fields actually NULL, content_hash present, and the row
    carries the expected slug/title/display_order. Deep semantic checks
    (R-3RULE-* / R-NARRATIVE-* / R-CHAR-range / R-DRAWER-no-sd-drawer /
    diff-delta) live in scripts/audit_meta_mlsd_3rule.py and are the canonical
    post-seed gate.
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

    # Populated-fields contract for oral_narrative (sd41-mirrored floors:
    # overview/formulas/cheat_sheet >= 200, dataflow >= 4000).
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
        f"     populated: overview={len(overview or '')} "
        f"dataflow={len(dataflow or '')} formulas={len(formulas or '')} "
        f"cheat_sheet={len(cheat or '')}"
    )
    print(
        f"     nulled: architecture="
        f"{'NULL' if architecture is None else len(architecture)} "
        f"production_constraints="
        f"{'NULL' if prod_cons is None else len(prod_cons)} "
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
