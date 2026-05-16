"""Seed: T-P0-869 [Meta-MLSD] Weapon Ads Classifier Golden -> system_designs.

INSERTs (or idempotently updates) the canonical Meta MLSD Weapon Ads Classifier
golden example as ``system_designs(slug='meta-weapon-ads-golden')``,
drawer-reachable via ``sd://meta-weapon-ads-golden``. This is a **T&S
classification** golden (NOT RecSys), sibling of ``sd://meta-reels-golden`` and
``sd://meta-top3-comments-golden``. Cross-link via cd://96 §1/§3 drawers.

T-P0-894 archetype migration (2026-05-16): document_archetype migrated from
``structured_reference`` (10-field shape, ~51KB across overview/architecture/
dataflow/formulas/production_constraints/tradeoffs/defense/verbal_outline/
cheat_sheet) to ``oral_narrative``, mirroring the sd41 golden template
established by T-P1-875 + T-P0-892. Per the archetype's contract in
``schemas/meta_mlsd_canonical.yaml`` (``document_archetypes.values.oral_narrative``):

  - ``dataflow`` carries a single continuous 第一人称 45-min 口播稿 (8 sections:
    开场 Framing / Data & Label / Features / Model / 冷启动 / Evaluation /
    Serving / Wrap).
  - ``overview`` / ``formulas`` / ``cheat_sheet`` are slim anchors.
  - ``architecture`` / ``production_constraints`` / ``tradeoffs`` / ``defense``
    / ``verbal_outline`` are NULL by design -- their content lives inlined in
    the dataflow narrative (立场 + trade-off + Strong Moment + verbatim).
    ``verbal_outline`` is populated separately and authoritatively by
    ``scripts/seed_meta_weapon_ads_golden_verbal_outline.py`` (T-P0-894 part B),
    a verbal-only seed that opts this oral_narrative row INTO a speaking
    skeleton for the SystemDesignDrawer (which renders verbal_outline first
    since T-P0-891). This main seed NULLs it; run the verbal seed last.

Rationale: the structured_reference shape spread the same Weapon-Ads insights
(bidirectional liability asymmetry / multi-layer adversarial / admission-posture
upstream / legal-adjacent boundary) across overview -> architecture -> dataflow
-> defense, each restating the others, and tripped R-CHAR-range +
R-NARRATIVE-bold-density on the 11.6KB dataflow. The oral_narrative shape
consolidates everything into one continuous oral-recital script; the audit
(scripts/audit_meta_mlsd_3rule.py) skips R-CHAR-range / R-NARRATIVE / the
nullable fields for oral_narrative and only enforces dataflow >= 4000 chars +
the section-level 3-rule.

The diff-delta baseline for this oral_narrative instance is recorded on the
``meta_mlsd_canonical.yaml`` instance as ``baseline_chars_post_migration:
11607`` (the structured_reference dataflow size at migration time -- the new
floor against which future deletions are gated; the migration commit itself is
exempt).

A pre-migration safety backup exists at
``data/backups/mle_prep_pre_weapon_komantxe_20260514_112637.db`` (revert path
if the oral_narrative content is rejected on review).

Idempotent: re-running upserts in place by ``slug``. Sentinel-based UPSERT
keyed on ``slug='meta-weapon-ads-golden'``. Two consecutive runs leave the DB
byte-identical (the row payload is fully deterministic).

Usage::

    python scripts/seed_meta_weapon_ads_golden_sd.py [--db data/mle_prep.db] [--dry-run]
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

SLUG = "meta-weapon-ads-golden"
TITLE = (
    "Meta MLSD Golden Example: Weapon Ads Classifier "
    "(T&S classification, 45min walkthrough)"
)
SUBTITLE = (
    "Meta MLSD Golden Example — 第一人称完整 45min 口播稿 "
    "(因果链 + 立场+trade-off + twist 在 body 兑现 三原则). "
    "T&S classification 题型 (admission cascade, NOT binary classifier); "
    "4-twist framing (bidirectional liability asymmetry / multi-layer "
    "adversarial / admission posture upstream / legal-adjacent boundary). "
    "方法论 (Strong Moment 调度, ML-native vocab, 8 meta-rules, E4/E5) 在 cd://96。"
)
DISPLAY_ORDER = 132
SOURCE_PATH = "docs/prep/meta_mlsd_2026-05-13_weapon_ads/source_06_weapon_ads_classifier_rewritten.md"

# T-P0-894: this seed produces an oral_narrative archetype document. See
# schemas/meta_mlsd_canonical.yaml > document_archetypes.values.oral_narrative.
DOCUMENT_ARCHETYPE = "oral_narrative"


OVERVIEW = """\
# Weapon Ads Classifier — 45min Golden 口播稿

按"因果链 + 立场+trade-off + twist 在 body 兑现" 三原则写成的完整第一人称口播稿。完整 8 段台词在 `dataflow` tab; cascade calibration / disagreement-aware label / hard-neg shortcut audit 三个公式 anchor 在 `formulas`; 数字 anchor + firm-claim register + Design Doc 强调话术在 `cheat_sheet`。方法论 (timing skeleton, Strong Moment 调度, ML-native vocab YES/NO, 8 meta-rules, E4/E5 boundary) 在 `cd://96` 主 hub, 此 row 只承载 Weapon Ads 这一题的 solution。

这道题我一上来就 reframe: 它不是一个二分类器, 是一个 **T&S admission cascade**——模型产出 calibrated P(weapon), 喂给 admission-policy 层做 allow / limit / block。四条 driving twist 在 framing 段就 declarative 立起来, 后续每个 component 兑现:

1. **Bidirectional liability asymmetry** — false-positive (砍掉合法持牌 gun-store 广告) 与 false-negative (放过非法私枪交易) 的法律代价不对称, 而且这个不对称 flips by jurisdiction (Texas FP 贵 / New York FN 贵)。落地: per-region calibrated threshold, 不是单一全局 cutoff。
2. **Multi-modal multi-layer adversarial** — 对手 rotate the medium: 文字搬进图、landing page cloaking、seller 身份轮换。落地: OCR + CLIP + seller-graph 三 modality + 每周对抗 retrain。
3. **Platform admission posture is upstream** — 模型不直接 take-down, 它产出的 posterior 要和 jurisdiction / seller posture compose。落地: cascade 每 stage calibrate 到同一 P(weapon) scale, threshold 才能跨 stage 组合。
4. **Legal-adjacent boundary IS the ML hard problem** — sport-knife / antique / 持牌 seller 那条边界才是真难点, 不是那把明显的步枪。落地: disagreement-aware label + counterfactual hard-neg shortcut audit。

整体方案: 3-stage admission cascade (cheap pre-screen → multi-modal main tower → human escalation), 全 stage shared-scale calibrated, main tower late-fusion concat + classification / uncertainty 双 head。"""


DATAFLOW = """\
# 完整 45min 口播稿 (第一人称, 8 段连续)

> Section 标题只是导航用, 真讲的时候是连续说下来的。每段串因果链, 每立场挂 trade-off, framing 立的四个 twist (liability asymmetry / multi-layer adversarial / admission posture / legal-adjacent boundary) 在 body 里逐一兑现。

---

## 开场 · Framing

"好, 这道 Weapon Ads 的题, 我开口第一件事是 reframe: 我不会把它做成一个'广告里有没有枪'的二分类器, 我把它 formulate 成一个 **T&S admission cascade**——模型产出的是一个 calibrated 的 P(weapon), 真正做 allow / limit / block 决定的是上游的 admission-policy 层。这个 reframe 本身就是这题的 senior signal, 因为它决定了后面 calibration、threshold、label 全都不一样。

我先 confirm 几个边界。规模上, 我假设每天几百万条 creative submission, 跨 O(100) 个 regulatory regime, 每个 region 的 weapon-ad base rate 在 0.05% 到 0.5% 之间, imbalance 真实但不极端。SLA 上, cheap stage 在 submission 时同步出结果 p99 < 5 ms, multi-modal main stage 异步几秒内 p99 < 80 ms, uncertain 的进 human review, 4 小时 SLA。

然后是这题和一道普通 classification 不一样的地方, 我认为有四个 twist, 我现在就 declarative 立起来, body 里逐个兑现。第一, **bidirectional liability asymmetry**——砍掉一个合法持牌 gun-store 广告是 regulatory complaint, 放过一个非法私枪交易是 DOJ subpoena, 两边代价不对称, 而且这个不对称会 flips by jurisdiction。第二, **multi-modal multi-layer adversarial**——对手会 rotate the medium, 价格搬进图里、违禁词转写、landing page cloaking、seller 换号。第三, **platform admission posture is upstream**——我产出的不是动作, 是一个要和 policy 组合的 posterior。第四, 也是我认为这题最 signature 的——**legal-adjacent boundary 才是真正的 ML 难点**, 难的不是那把明显的步枪, 是 sport-knife、antique collectible、持牌 seller 这条边界。

整体方案我先给一句: 一个 3-stage 的 admission cascade, cheap pre-screen 砍掉绝大多数, multi-modal main tower 精算, human escalation 兜 uncertain middle, 三个 stage 全部 calibrate 到同一个 P(weapon) scale。这是我的 framing, 你想我先深入 label, 还是 model 和 serving?"

---

## Data & Label

"我从 label 开始, 因为这题最 non-trivial 的就是 label, 不是 model。

核心难点是 legal-adjacent middle 上 reviewer 自己就会 disagree, 而那个 disagreement 恰恰是 policy 层需要的信号。所以我**特意不做 majority-vote**。我的处理是 disagreement-aware label: 一个 item 被 n 个 reviewer 标过, 我记三个量——consensus label 当 classification target, 一个随 disagreement variance 下调的 sample-weight, 以及 variance 本身当 uncertainty head 的监督目标。这比 majority-vote 严格更强, **代价是**多养一个 uncertainty head 和 label store 里的 per-reviewer skill weight, 但换来的是 legal-adjacent middle 上不丢信息。reviewer 三人以上一致才算 confident positive / negative; split 的进 disagreement region, 同时 promote 到 rolling eval set 打 ambiguous-middle tag。

label 稀缺这一侧, 我会上 **LLM-multimodal teacher distillation**: teacher 在 non-reviewed 长尾上出 soft label, student 用 KL 对 soft label 蒸馏、human hard label 加权更高。student 大概保 ~98% 的 teacher recall, 成本只有 ~5%, 这是让每天几百万条的 cascade 经济上跑得起来的关键。代价是 teacher 贵, 所以 distill 只能 monthly, 不是 weekly。

eval 这块我有一个不能 collapse 的纪律——**三套 eval set, 各回答不同问题**: frozen golden set 永不更新, 回答'有没有过 regulatory bar'; rolling weekly set 每周一从上周 reviewed sample 刷新, 回答'这周的流量上表现如何'; adversarial red-team set 持续更新, 回答'对主动 evasion 扛不扛'。把三套合成一套是常见错误——一个 model 在 frozen 上好看, 在 adversarial 上可能已经被打穿了。imbalance 用分层采样 + class-weighted loss; 这里没有 bandit exploration, 因为一个 false negative 的代价是 regulatory, 不是一次 UX 实验。"

---

## Features

"feature 我按 user / content / context / cross 四类拆, 但这题最重的象限是 item-side 加 seller-side 的 relational。

ad creative (item-side, 主象限): OCR 抽出的图内文字——这是 multi-modal twist 在 feature 层兑现的地方, 专门打 caption-only obfuscation; CLIP image embedding 用对抗增强 fine-tune; caption + landing-page 文本, 配 crawler-as-end-user parity 检 cloaking。

seller (relational 象限, 这是 seller-graph twist 落地的地方): 历史 violation count 加 days-since-last 衰减; **2-hop seller-graph 特征**——共享支付工具、共享地址、共享 device fingerprint, 用 GNN 聚合, 每 6 小时刷新一次; verification status (FFL 持牌 / 实名 / 都不是)。

context: region (jurisdiction-coded, 给 per-region threshold table 用)、placement、与 weapon-interest audience 的 overlap。cross: 这个 seller 是不是 re-upload 了被下架过的同一张图、本 caption 和同一 seller-graph cluster 历史违规 caption 的 edit-distance。

我想强调一个 critical distinction: seller-graph 特征是 per-(seller, time) 现算的, 6 小时一刷。这就是为什么一个 multimodal-only 的分类器不够——没有 identity propagation, 一个被封 seller 换号重生就清零了, 分类器永远看不到那条 link。这条 twist 我会在 model 段再兑现一次。"

---

## Model

"model 我做 3-stage cascade, 不做单一大模型。

**我选 cascade 不选 end-to-end**, 因为它同时是 serving-cost decomposition (cheap stage 吸收 >=95% 流量) 和 calibration decomposition (每个 stage precision-recall 干净)。单一 end-to-end 会逼每条 creative 都过 OCR + CLIP + seller-graph + LLM teacher, 在 Meta ads QPS 上贵两个数量级。代价是三个 calibration window 加一个 stage-skew 周审计; 只有 compute 无约束时才 switch 回 end-to-end, 而这不是我们的 regime。

stage-1 cheap pre-screen 用一个 distilled student 同步跑, 砍掉 >=95% 明显非武器的流量; stage-2 main tower 只看活下来的 2-5%; stage-3 human escalation 接 uncertain middle, 4 小时 SLA。

main tower 我用 **late-fusion concat** over OCR / CLIP / seller-graph embedding, 不用 early fusion——因为 OCR text 会随对手切 modality 而 drop in and out, late fusion 在某个 modality 缺失时 degrade gracefully。代价是 jointly-aligned modality 上有一点点 loss; 只有当一个 end-to-end transformer 在 adversarial set 上比 late-fusion concat 高 >=2 个点才 switch, 这个规模上还没出现过。

两个 head: classification head BCE + temperature-scaled, uncertainty head 直接回归 disagreement variance——不是 Bayesian-dropout MC, 就是一个直接监督目标, 这是拿 routing 信号最便宜的工程做法。两个 head 的组合在 policy 边界做, 不塞进单一 weighted loss——把 uncertainty 揉进一个 composite score 是 category error。

cascade 能 work 的关键性质是 **shared-scale calibration**: 每个 stage 的 logit per-region temperature-scale 到同一个 calibrated posterior, 不只是同一个 ranking。没有这个, stage-1 的 threshold 和 stage-2 的 threshold 代表不同的先验概率, cascade thresholds 就不能 compose。这正是 framing 里 admission-posture twist 承诺的东西在 model 层的兑现。"

---

## 冷启动 (承接 model)

"冷启动这题主要是 new-seller cold-start, 不是 new-item。

一个全新 seller 没有历史 violation、没有 graph 邻居, naive 做法会把它当干净的, 这恰恰是对手要的。**我的处理是**让 2-hop seller-graph 用 verified-identity prior 兜底——即使这个账号是新的, 它共享的支付工具 / 地址 / device 往往不是新的, GNN 沿这些边传播过来的 risk prior 就是冷启动期唯一相对无偏的信号。fallback 顺序我特意写清楚: 先 graph-propagated prior, 再 region x category 的 base rate, 最后才是全局 prior, 不会直接 fallback 到全局 (太糊)。

verified FFL seller 走一条轻量的快速通道, 但仍然过 cheap stage, 因为'持牌'不等于'这条 creative 合规'。bandit 我知道是选项, 但这里 explore 的代价是 regulatory, 我点到为止, 不展开。"

---

## Evaluation

"evaluation 我分三层, 而且我会主动讲监控顺序, 因为这是 E5 的 boundary signal。

第一, **hard-neg shortcut counterfactual audit, 每周**。对每个 hard-neg 我扰动一个属性——换 seller 身份、换 caption、换 landing-page 域名——量 prediction shift。如果在一个 non-causal 属性 (比如 caption 和图没变只换了 seller 名) 上 prediction 翻了, 模型在走捷径。shortcut rate 超 5% 就触发下次 retrain 的 feature-importance re-weight。这个比 precision-recall 退化更早, 因为它抓的是'对的答案但错的理由'。

第二, **三套 eval set 持续跑**: frozen golden 每晚当 regulatory-bar tracker, rolling weekly 周一刷新后读, adversarial red-team 持续从 classifier-missed 里挖新 evasion。不要 collapse 成一个数。

第三, **online prediction-distribution drift, 每小时**, day-over-day KL divergence 抓 base-rate shift, 这是最 leading 的指标, 比三套 eval set 还早。大多数候选只会说'monitor AUC', 这条是 senior signal。

offline metric 我按 region 和 seller-verification segment 切, 因为 base rate 和代价结构都随 jurisdiction 变。calibration 我每晚用 frozen golden 上的 ECE 查 drift, 任何单个 (stage, region) cell 的 ECE 破 2% 就 halt threshold rotation——这是 circuit breaker, 不是人工 review。"

---

## Serving / Logging

"serving 和 logging 我给几个最在意的点, 不展开。

latency 三档: cheap stage 同步 p99 < 5 ms, main stage 异步 p99 < 80 ms, human queue 4 小时 SLA; 提交高峰 (选举季、监管 deadline) 大概 10x 平均。seller-graph 必须 6 小时一刷, 否则被封 seller 换号重生比 graph 看见还快——这条是 feature 段那个 relational twist 在 serving 层的最后一次兑现。

最关键的运维面我认为不是 model weight, 是 **policy threshold rollout**。监管环境变得比 ML release cadence 快, 所以 threshold rotation 是一条独立的 change-management lane: 一个 region-specific threshold 走 shadow + 1% / 5% / 25% / 100% canary, 三个 guardrail 任一破就自动 halt——per-region ECE > 2%、FFL-seller FP-rate 超 baseline + 10%、adversarial FN-rate 超 baseline + 5%。train-serving 一致性上, calibration temperature 离线在 validation set 上算、线上原样应用, 周期性用 online-served data 重算校对, 偏差 > 5% 冻结 threshold rotation。"

---

## Wrap

"我 zoom out 收一下, 然后说三个我最担心的 risk。

整体是一个 3-stage admission cascade, OCR + CLIP + seller-graph 三 modality late-fusion, classification + uncertainty 双 head, 全 stage shared-scale calibrated, eval 覆盖 frozen / rolling / adversarial 三套加每周 counterfactual shortcut audit, policy threshold 走独立 circuit-breaker rollout lane。

三个 risk。第一, seller-graph 刷新窗口设太宽 (我们踩过 24 小时的坑), 被封 seller 在窗口内换号清掉分类器, 修法是 6 小时刷新 + submission 时的 payment-instrument hash join。第二, cascade 在 frozen set 上看着 calibrated, 某个 region base-rate 一漂就在 rolling weekly 上 silently miscalibrated, 修法是 per-region temperature + 每晚 ECE drift gate, 不是单一全局 recalibration。第三, 也是最重要的——legal-adjacent middle 上的 disagreement 如果被 majority-vote 抹掉, 模型会在边界上自信地犯错, 这个 alarm 靠 uncertainty head 的 routing 量 + adversarial red-team set 来抓。

这些是我的设计, 哪一块你想让我再深入?"
"""


FORMULAS = """\
# 三个公式 anchor (口播稿对应的形式化, 面试官追问时打开)

> 口播稿原文在 `dataflow` tab; 此处只放 cascade calibration / disagreement-aware label / hard-neg shortcut audit 三个 anchor 的精确定义, 面试官追问公式时打开。

## Cascade calibration (shared-scale temperature)

每个 stage `s` 在 region `r` 上学一个 temperature `T_{s,r}` (held-out validation set):

```
P_s(weapon | x, region=r) = sigmoid(z_s / T_{s,r})
```

强制的性质: 对任意 human-reviewed `x`, `P_1(weapon|x,r) ~= P_2(weapon|x,r)` 在重叠 support 上成立, cascade threshold 才能 compose。等价地, frozen golden set 上每 region ECE 卡 2%:

```
ECE_{s,r} = sum_b | acc(bucket_b) - mean_pred(bucket_b) | <= 0.02
```

任一 (stage, region) cell 破 2%, threshold rotation pipeline halt (circuit breaker, 非人工 review)。

## Disagreement-aware label

一个 item 被 `n` 个 reviewer 标, 投票 `y_i in {0,1}`, label store 记三个量:

```
y_consensus   = round(mean(y_i))            # classification target
w_consensus   = 1 - 2 * variance(y_i)       # sample-weight, split 时低
variance(y_i) = mean(y_i) * (1 - mean(y_i)) # uncertainty target
```

classification head 训 `(y_consensus, w_consensus)`, uncertainty head 直接训 `variance(y_i)`。严格强于 majority-vote, 因为 variance 被当独立监督信号保留, 没被丢掉。

## Hard-neg shortcut counterfactual audit

对每个 hard-neg `x` (高 P(weapon)、human-labeled negative), 每次扰动一个属性生成反事实 `x'`, 量 shift:

```
shift_attr(x, attr) = | P(weapon|x) - P(weapon|x_perturbed(attr)) |
```

若 non-causal 属性 (caption + 图不变只换 seller 身份) 上 `shift_attr > 0.3`, 模型在走捷径。每周抽 ~1000 hard-neg 跑, shortcut rate > 5% 触发下次 retrain 的 feature-importance re-weight。"""


CHEAT_SHEET = """\
# 30-sec pre-walk-in checklist — Weapon-Ads-only

> 方法论 (timing skeleton, 元结构, 8 meta-rules, E4/E5 boundary, drift recovery vocab) 在 `cd://96` §1 / §5 / §6 / §8。此处只放 Weapon-Ads 特有的 anchor 数 + firm-claim register + Design Doc 强调话术, 进面前 30 秒过一遍。

## 数字 anchor (说出来时声音里就有数)

- **3-stage cascade**: cheap pre-screen → multi-modal main → human escalation
- **>=95% / 2-5%**: cheap stage 吸收占比 / main tower 看到的占比
- **p99 < 5 ms / p99 < 80 ms / 4 小时 SLA**: 三档 latency anchor
- **6 小时 seller-graph 刷新, weekly main retrain, nightly calibration drift, monthly LLM teacher distill**: tiered cadence
- **ECE <= 2% per region**: policy rollout 的 circuit-breaker 阈
- **shortcut rate > 5%**: counterfactual audit 触发 re-weight 的阈
- **rollout 1% / 5% / 25% / 100% + 3 guardrail (ECE / FFL-FP / adversarial-FN)**: policy-threshold change-management lane
- **student ~98% teacher recall @ ~5% cost**: LLM-teacher distill 经济性
- **O(100) regions, base rate 0.05%-0.5%**: scale anchor

## Firm-claim register (整场至多说 1 次)

- "**这不是二分类器, 是 T&S admission cascade**——模型产出 calibrated P(weapon), 决策在 policy 层。" (开场 reframe 立场)
- "**liability asymmetry flips by jurisdiction**——Texas FP 贵, New York FN 贵, 所以 per-region threshold 不是全局 cutoff。" (Twist 1 callback)
- "**late fusion 在某 modality 缺失时 degrade gracefully——这正是 trio main tower 需要的性质。**" (Twist 2 callback)
- "**cascade thresholds compose 的前提是每个 stage calibrate 到同一个 posterior。**" (Twist 3 callback)
- "**disagreement-aware label 严格强于 majority-vote, 因为 legal-adjacent middle 上 variance 就是信号。**" (Twist 4 callback)
- "**policy threshold rotate 比 model weight 频繁——它是独立的 change-management lane。**" (Wrap production 立场)

## 复用范围

此 row 的 3-stage cascade + shared-scale calibration + OCR/CLIP/seller-graph trio + disagreement-aware label + 三套 eval set + counterfactual shortcut audit + circuit-breaker policy rollout 是 **T&S classification** 这一题的 carve-up。RecSys / list-level / bilateral-matching 等其他 Meta MLSD 题型的 mapping 见 `cd://96` 主 hub (不在此 row 内 bundle sibling)。

---

## Design Doc 强调话术 (interview / Design Doc / Code Review 通用的收尾句)

**这 4 句 verbatim 说出来**:

1. **「采用 3-stage admission cascade，每个 stage 的输出 calibrated 到 shared P(weapon) posterior，policy thresholds 在 cascade 上可组合。」**
2. **「OCR + CLIP + seller-graph 三 modality 用 late-fusion concat，单模态缺失时模型 degrade gracefully，对抗性 evasion 不会通过单一通道击穿。」**
3. **「Disagreement-aware label：reviewer variance 进入 uncertainty head，不被 majority-vote 抹掉；在 legal-adjacent middle 上严格强于 majority-vote。」**
4. **「Three eval-sets (frozen / rolling / adversarial) 各 gate 一个 production action；Policy threshold rotation 是独立的 change-management lane，不和 model weights 共用 release cadence。」**

四句分别是: 架构承诺 (cascade-as-decomposition + shared-scale calibration)、多模态鲁棒承诺 (late fusion + 对抗训练)、label-layer 承诺 (disagreement 当监督信号不当噪声)、production-process 承诺 (eval 纪律 + policy rollout 独立 lane) ——这是 E5 boundary signal: 你懂 ML metric / regulatory exposure / policy posture 三者关系, 拒绝把它们 collapse 成一个数。"""


# T-P0-894: oral_narrative archetype NULLs these 5 fields. Their content lives
# inlined in DATAFLOW (the 8-section 口播稿). verbal_outline is populated
# separately and authoritatively by
# scripts/seed_meta_weapon_ads_golden_verbal_outline.py (run it last).
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
    """Archetype-aware seed-side validation (mirrors sd41's oral_narrative gate).

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
