"""Seed: T-P0-853 [Meta-MLSD] Top-3 Comments Golden -> system_designs.

INSERTs (or idempotently updates) the canonical Meta MLSD Top-3 Comments
golden example as ``system_designs(slug='meta-top3-comments-golden')``,
drawer-reachable via ``sd://meta-top3-comments-golden``. Sourced from
``docs/prep/meta_mlsd_2026-05-12_top3/source_04_top3_comments_golden.md``
(user-authored Discord msg 1503871555216605214 Part 4 Golden Answer + Part 5
Mock Checklist + msg 1503874418802163744 Bias Tower / Shadow Logging reference).

T-P0-868 reseed (2026-05-13): per schemas/meta_mlsd_canonical.yaml, the
methodology homepage moved to cd96 and sd-golden is now solution-only.
Replaced overview 整体节奏哲学 prose (R-FORBID-rhythm-philosophy) with a
2-paragraph solution anchor + Top-3-Comments-specific 4-Strong-Moment slot
map; stripped any 'why this is strong' meta-prose from defense
(R-FORBID-why-this-is-strong); consolidated verbal_outline + cheat_sheet
to Top-3-Comments-specific anchors only (R-XPAGE-{cheatsheet,verbal}-no-
cd96-dup); added Decision summary blocks to architecture / dataflow /
production_constraints / tradeoffs / defense for section-level 3-rule
pass. NO drawer header (R-DRAWER-no-sd-drawer).

Target row shape (9 prose columns, all > 200 chars, schema char ranges
per sd_golden.fields):
  - overview                : 2-paragraph solution anchor (what / 3 twists / 4-slot map)
  - architecture            : 2-stage point-wise ranking + MMR set-selection reranker + bias tower
  - dataflow                : 4-section verbatim walk (framing / metrics / labels / features)
  - formulas                : label schema (L1-L4) + negative sampling + multi-task conflict + score combine
  - production_constraints  : Section 5.3 serving + tiered refresh + skew defense
  - tradeoffs               : 8 tradeoffs ("I pick A because X, costs Y, switches to B if Z")
  - defense                 : 4 Strong Moment verbatim + monitoring + A/B + loop closure; NO 'why this is strong' meta-prose
  - verbal_outline          : Top-3-specific entry phrases + drift lines (methodology lives in cd://96)
  - cheat_sheet             : Top-3-only quantification anchors + firm-claim register + 4 Design Doc 强调话术 (cd://96 owns timing skeleton + 8 meta-rules)

Architecture and production_constraints both embed a short Bias Tower /
Shadow-Logging digest with an anchor sentence pointing to fr-node
``meta-prep/system-design-must-knows/popularity-bias-debiasing`` (id=266)
for the 深版 walkthrough (T-P0-854 owns that 深版).

Idempotent: re-running upserts in place by `slug`. Sentinel-based UPSERT
keyed on `slug='meta-top3-comments-golden'`.

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

This golden walks one verbatim 45-minute interview for **Top-3 Comments under a Post**: a viewer-primary set-selection problem where retrieval is trivially bounded by the post's own comment pool, so the design lives entirely in **ranking + list-level reranking**. The unique angle is that **three intrinsic twists** -- comment-is-not-an-item, early-comment time-bias, and community-health-as-guardrail -- drive almost every downstream decision, and the answer is to put all three on the table inside the first 60 seconds, then revisit each as a Strong Moment later. Methodology (timing skeleton, ML-native vocabulary YES/NO, 8 偏好节奏 meta-rules, E4/E5 boundary) lives in `cd://96`; this row owns only the solution.

## Twist 1 -- Comment is not a generic item

Comments are ultra-short text whose authorship is a user-graph node, so the dominant signal is social, not text. **I pick** text + social fused representation (caption / hashtag-style mini-BERT for the body, commenter sub-entity embedding for identity, viewer x commenter follow / past-engagement as cross features), feeding the L2 ranker's main tower. Costs: an extra commenter-side embedding pipeline maintained alongside the post-side index. **Switches to** pure text two-tower retrieval only if the post pool exceeds ~10k comments per post -- not the in-feed regime. This is where the "ranker beats two-tower because ranker can see viewer x commenter interaction terms" claim pays off.

## Twist 2 -- Early-comment time-bias

Comments posted in the first minutes of a post's life accumulate disproportionate impressions, so raw engagement counts confound time-of-arrival with quality. **I pick** **engagement velocity (rate, not count)** as the time-debiased label and feature, plus a **5% per-session bandit exploration budget** to surface late-arriving comments. Costs: streaming engagement-rate compute (1-5 min cadence) and a UX cost of late-comment exposure. **Switches to** simple count-based ranking only if velocity infra is unavailable in week 1, but the time-bias mitigation is the twist this Strong Moment hosts.

## Twist 3 -- Community-health is a guardrail, not a head

Toxicity / abuse / harassment are disqualifying, not "less engagement". **I pick** an **independent abuse model + toxicity hard filter pre-ranker** (NOT shared weights with the engagement ranker), with tiered action (hard filter for confident, hard demote for uncertain). Costs: a second model trained on weekly retrain cadence to fight adversarial drift. **Switches to** soft loss term only if abuse model precision collapses below 0.8 -- but treating compliance as a loss term is a category error.

## 4 Strong Moment slots (pre-allocated, do NOT improvise)

| # | Time   | Theme                                  | Top-3-Comments-specific twist anchor                                            |
|---|--------|----------------------------------------|---------------------------------------------------------------------------------|
| 1 | 0-1    | 3 unique twists framing                | "set-selection not pure ranking" + 3 twists + 15/25 time plan                   |
| 2 | 8-12   | Selection-bias 三阶 negative label     | IPS-weighted exposed-not-engaged + 5% bandit unexposed + hard-neg mining        |
| 3 | 15-21  | Bias Tower + MMR vs DPP                | shallow additive bias tower + mask-at-inference + MMR with hard quota across 3 axes |
| 4 | 31-35  | 4 monitoring signals (leading vs lagging) | prediction distribution shift earlier than engagement metric; list-level A/B   |

The dataflow / defense / tradeoffs columns are this row's solution body; verbal_outline + cheat_sheet hold only Top-3-Comments-specific anchors. Anything else (rhythm rules, vocab YES/NO, E4/E5 line) belongs in `cd://96`.
"""


ARCHITECTURE = """\
# Architecture: 2-stage Pointwise Ranking + MMR Set-Selection Reranker + Shallow Bias Tower

## Decision summary (the architectural twist)

**I pick** a 2-stage point-wise ranking funnel (cheap pre-rank -> deep rank) followed by an **MMR list-level reranker with hard quota across 3 axes (commenter / sentiment / topic)** -- the **unique angle** vs a generic ranker is the shallow additive **bias tower with mask-at-inference** that structurally decouples relevance from position / popularity / freshness bias. **This is where** the Bias-Tower-and-MMR-vs-DPP twist of Strong Moment #3 lives. Latency budget p99 < 200 ms over ~1000 candidates per request.

## Funnel (top-down, each layer budget explicit)

```
Pre-filter (toxicity hard filter + dedup, in-storage)  -> 1000 candidates
L1 pre-rank (GBDT, cheap features, weighted target)    -> top 100-200
L2 deep rank (MMOE + shallow bias tower)               -> point-wise scores
Reranker (MMR with hard quota across 3 axes)           -> top 3
```

## L2 ranker detail (the core -- expand ~90s)

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
|           MASKED at inference  <- key      |
+--------------------------------------------+
```

**Multi-task start point**: shared bottom + multi heads + composite label; **upgrade to MMOE only if negative transfer appears** -- do not default to MMOE on day 1. Loss weights are **locked by business context** (comment lift value + risk budget), **NOT uncertainty weighting** -- because the weight is a product decision, not a statistical estimate.

## Reranker: MMR not DPP (the most important architectural trade-off)

- **Why MMR**: for n=3 the list is too short for DPP's set-level optimization -- the 3-item determinant is dominated by any single pairwise cosine, costing DPP its theoretical edge
- **Method**: MMR across 3 axes (commenter / sentiment / topic) + **hard quota** (no 2 same commenter, <=1 OP self-reply)
- **Future upgrade signal**: switches to DPP with learned kernel **when list expands to top-10+**; this is the senior way to write the trade-off -- not "MMR is better", but "MMR for this regime, DPP if regime changes"

==> Section-stitch: the 3 heads map back to Section 2's 3 proxies; the shallow tower delivers what Section 3 promised on debias.

## Bias Tower digest (this section self-contained -- deep version in fr-node)

**3-sentence core (verbatim from user reference §1-§3)**:

1. **Additive structure + capacity bottleneck**: `logit = main_tower(content, user, ctx) + bias_tower(bias_features)`, main tower deep (MMoE), bias tower shallow (1-2 layers / linear). Bias tower input is **bias features only** (position / device / slot type / isAds). The shallow inductive bias **cannot absorb content signal**, leaving it room only for additive bias -> the main tower is forced to learn real relevance.
2. **Mask-at-inference**: at training time the bias tower sees real position; at inference the **bias term is zeroed entirely** (or position set to a fixed reference value). Companion training trick: position-feature dropout to make the model robust to missingness.
3. **Bias tower vs feature-input**: the bias tower is **additively separable**, so inference masking is well-defined; mixing position into the main tower causes content x position entanglement, distributional drift at inference, and position stealing gradient share. Theoretical equivalence (random position + dropout + regularization + large capacity) is exactly the hand-built bias-tower decomposition.

**Deep version in fr-node `""" + ANCHOR_FR_NODE + """`** -- covers isAds counterfactual vs context-feature distinction, shadow logging x bias tower coupling, and the 3-line mantra (architecture / inference / data debias, three layers all required); T-P0-854 owns that 深版.

## Architectural choices -> 3 twists (callback)

| Twist                       | Architectural choice                                                       |
|-----------------------------|----------------------------------------------------------------------------|
| Comment != item             | Comment text embedding @ creation + commenter sub-entity features in main tower |
| Time-bias                   | Engagement velocity feature (rate, not count) + shallow bias tower mask    |
| Adversarial / community     | Toxicity hard filter pre-ranker + **independent abuse model** (no shared weights) |
"""


DATAFLOW = """\
# Dataflow: Section 1-4 Verbatim (前段 14 min framing + metric + label + feature)

## Decision summary (the rhythm twist)

**I pick** a chronological 4-section walk over a component-by-component walk because **the core decision here is** time-allocation: 4 Strong Moments at fixed slots (0-1 framing / 8-12 label / 15-21 architecture / 31-35 monitoring), **this is where** E4 vs E5 wrap diverges. Latency: p99 < 200 ms at billion-QPS for hot post sessions, single-digit ms p99 for the streaming engagement-velocity feature.

## Section 1: Framing (90s)  <- Strong Moment #1

"L1 (user): **Viewer is the primary user** -- they consume comments and decide whether to engage. Commenter and OP are secondary stakeholders, folded into the joint-experience guardrail.

L2 (scale): **100M DAU, ~10% commenting rate, viral post peak 100x average, p99 < 200ms**.

L3 (twists with implications):

- **Comment != item** -> need text + social fused representation, commenter as sub-entity
- **Time-bias** -> engagement velocity (rate, not count) as feature, bandit explore late comments
- **Community health** -> independent abuse model + toxicity hard filter pre-ranker

L4 (ML formulation): **2-stage point-wise ranking** (cheap pre-rank -> deep rank) + **list-level reranking** (MMR for diversity). Retrieval is trivially bounded -- not expanded."

==> Section-stitch: each of these 3 twists hooks into a specific downstream metric or guardrail.

## Section 2: Metrics (60s)

"**L1 North-star**: **weekly commenter return rate** -- one number, not a parallel list. Captures 'see good top-3 -> willing to engage -> long-term return'.

**L2 Proxies (3, each with one-line alignment)**:

- Comment-area dwell time -> top-3 interesting -> user reads longer -> return up
- Reply rate triggered by top-3 -> top-3 sparks conversation -> commenter return up
- Self-comment rate after top-3 -> top-3 activates participation -> new-commenter return up

**List-level metric (top-3 is set selection)**:

- Top-3 **diversity score** (sentiment / commenter / topic, 3 axes)
- Set-level user satisfaction (post-view next-action distribution)

**L3 Guardrails (metric + threshold + enforcement mechanism)**:

- Toxicity rate < 0.5% -> hard filter pre-ranker
- Report rate per 1k impressions < X -> A/B halt criterion
- p99 latency < 200ms -> serving constraint
- Early-post exposure share -> fairness re-weight in loss
- Group-exposure gini -> fairness audit

**L4 Causal chain**: reply rate up -> users perceive conversation value in the comment area -> users return to engage -> weekly commenter return up."

==> Section-stitch: north-star and 3 proxies directly define the label schema -- the next section will land each one.

## Section 3: Labels (90s)  <- Strong Moment #2 (selection bias)

"**Positive label ladder**:

- L1 baseline (the dumbest version): binary engagement (like / reply within window)
- L2: weighted multi-signal (reply > like > view-completion)
- **L3 (I pick this level)**: engagement-to-impression ratio in rolling [T, T+1h] window
  - Trade-off: more complex than raw count, but **partial-debias of position bias**
- L4 (follow-up): multi-task labels with weighted heads

**Negative label (the core difficulty of this question -- selection bias)**:

- **Explicit**: dislike / report (strong signal, used directly)
- **Exposed-not-engaged**: standard negative
- **Unexposed**: treat as **unknown** + IPS-weighted + bandit-exploration backfill
  - Why not 'unexposed = negative': introduces massive false negatives (a good comment that simply wasn't surfaced)
  - Trade-off: engineering complexity, but theoretically correct

**Imbalance ladder (stop at L2, leave L3/L4 for follow-up)**:

- L1: stratified sampling
- L2: class-weighted loss

**Bias handling**: popularity / position / freshness -> **shallow bias tower, masked at serving** (YouTube 2019 design, more stable than masking input features because the model cannot reconstruct bias from other features).

**Leakage guard**: feature snapshot @ T, label observation @ [T, T+ΔT], **no overlap**."

==> Section-stitch: multi-task labels (engagement / quality / safety) define the number of heads the architecture in the next section will need.

## Section 4: Features (60s) -- 4-quadrant model

"**4-quadrant model, 3 per quadrant + 1 comment-specific**:

**User (viewer)**:

- Demographic + topic-preference embedding
- Viewer history comment-engagement rate
- Viewer sentiment preference (positive / debate / sarcasm)

**Item (comment + commenter sub-entity)** -- contains the comment-specific items:

- Comment text embedding (computed once at creation)
- **Early engagement velocity** (rate-based, time-debiased) <- corresponds to Section 1 time-bias twist
- **Commenter identity** (verified / OP / followed-by-viewer) <- corresponds to comment-is-not-item twist
- Toxicity / sentiment score (bonus, feeds quality head)

**Context**:

- Post topic + age
- Time of day + day of week
- Device + session intent

**Interaction (viewer x this specific comment)** -- the root of why ranking beats single-tower retrieval:

- Viewer x commenter follow relationship
- Semantic similarity (viewer's comment history vs this comment)
- Viewer's historical engagement with this commenter

**Critical distinction**: Interaction features are per-(user, item) pair, **recomputed per candidate at serving**. This is the root of why ranking beats two-tower retrieval -- two-tower can never compute user x item interaction, only a dot product."

==> Section-stitch: comment embedding feeds the L2 ranker main path; interaction features cross with user embedding in the DCN-style cross layer.
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


PRODUCTION_CONSTRAINTS = """\
# Production Constraints (Section 5.3 Serving + Shadow-Logging digest)

## Decision summary (the production twist)

**I pick** parallel feature prefetch in the candidate-retrieve stage + streaming engagement-velocity feature (1-5 min cadence) + shadow-feature logging + online-offline feature parity test + cache with 5-min TTL and high-engagement invalidation -- **this is where** time-bias mitigation and skew defense meet the wire. p99 < 200 ms over ~1000 candidates, viral peak 100x average, streaming feature single-digit ms p99.

## Section 5.3 Serving (~6 min, verbatim)

**Latency budget (p99 < 200ms, 5-layer breakdown)**:

| Stage                                            | Budget   |
|--------------------------------------------------|----------|
| Candidate retrieve + parallel feature prefetch   | **60 ms** |
| Storage-local pre-filter                         | **10 ms** |
| L2 ranker (DNN batch 100-200)                    | **80 ms** |
| Rerank feature fetch + MMR                       | **30 ms** |
| Aggregation + serialize                          | **20 ms** |
| **Total**                                        | **200 ms** |

**Key design**:

- **Feature prefetch issues RPCs in parallel during candidate retrieve** -- by ranker time the features are already in memory. That is why the 60ms stage runs prefetch instead of waiting for pre-filter to finish.
- Reranker spends only 30ms because MMR is essentially free at n=3; the overhead is the extra sentiment / commenter-group feature fetch.

## Tiered refresh strategy (5 cadences, not one-size-fits-all)

| Cadence              | What                                                                       |
|----------------------|----------------------------------------------------------------------------|
| **Streaming 1-5 min**| engagement velocity, recent counts, real-time toxicity flag                |
| Hourly batch         | aggregated like rate, cumulative stats                                     |
| Daily batch          | user profile, commenter reputation, topic preference                       |
| At creation          | comment text embedding (compute once, never recompute)                     |
| Daily / Quarterly    | ranker retrain (daily) / embedding model contrastive retrain (quarterly)   |

**Key**: **engagement velocity must be streaming** -- otherwise the time-bias mitigation promised in Section 1 cannot run. This is the **explicit accountability chain** from Section 1 framing's product promise to the serving section's streaming infra cost.

## Serving-skew prevention (2-piece industrial standard) + Cache

**2-piece skew defense**:

1. **Shadow feature logging**: at serving time, dump the actual feature values fed to the model; offline training consumes that log, **never recomputes** -> the only way to fully prevent skew.
2. **Online-offline feature parity test**: compute the same (user, item) pair through online and offline pipelines, alert when diff > threshold -- the audit gate that polices shadow logging.

**Cache**: hot-post results cached at session start, **5-min TTL + invalidation triggered by newly-high-engagement comments**. Under 100x viral peak, cache is the latency lifeline.

## Shadow Logging + Train-Serve Skew digest (self-contained -- deep version in fr-node)

**4 sources distilled (verbatim from user reference §5)**:

1. Train / serve code-path mismatch (Python vs C++)
2. Time travel: training feature leaks future
3. Data-source / default-value / null-handling drift
4. **Bias feature uses real value at train, mask at serve -- distribution mismatch** -- directly coupled to the architecture section's bias tower

**Shadow logging 2-piece core (verbatim from user reference §6)**:

- Guarantees train / serve features are **100% identical** (same code computes both)
- **Point-in-time correct, no future leakage**; bias features (position / device) are recorded faithfully so the bias-tower training distribution aligns -- otherwise the architecture section's mask-at-inference is broken by skew at the data layer.

**Deep version in fr-node `""" + ANCHOR_FR_NODE + """`** -- covers shadow logging engineering details (async queue Kafka/Pub-Sub, non-blocking serving / streaming label joiner Flink/Beam, request_id correlation of behavior / continuous monitoring of logged feature distribution vs serving real-time distribution, alerts); T-P0-854 owns that 深版.

## Production scar (E4 senior signal -- one or two sentences total)

- "**In my past work**, we found that when shadow logging was first launched without an async queue, inline writes pushed serving p99 up by 30%. The fix was fire-and-forget pub-sub."
- "**One thing we learned the hard way**: the bias tower mask-at-inference step had forgotten to apply position-feature dropout in training. After deployment the model collapsed on position=missing, because the test-time distribution was out-of-distribution."
"""


TRADEOFFS = """\
# Tradeoffs (8 decision points -- each "I pick A because X, costs Y, switches to B if Z")

## Decision summary (the tradeoff twist)

8 tradeoffs follow, each in the form **"I pick A because X, costs Y, switches to B if Z"**. **This is where** the architectural twists meet concrete numbers: ~1000 candidate batch, p99 < 200ms, 5% bandit exploration, daily ranker retrain, weekly abuse-model retrain, MMR at n=3 vs DPP at n=10+.

## 1. Multi-task conflict: hard pre-filter + soft penalty  vs  PCGrad / reward shaping

**I pick** hard constraint via pre-filter + soft penalty in the engagement head.

| Option                                            | Pros                                    | Cons                                                |
|---------------------------------------------------|-----------------------------------------|-----------------------------------------------------|
| **Pre-filter + soft penalty (pick)**              | Easy audit, clear failure mode, E4 standard answer | Pre-filter threshold is a product decision, not statistical |
| PCGrad / GradVac                                  | Automatic conflict handling             | Complexity not worth it; top-3 ranking is not high-competitive multi-task |
| Reward shaping into single label                  | Easy implementation                     | Loses eval diagnostic power, monitor head gone     |

**Why pick**: "Top-3 ranking is not GradNorm-class high-competitive multi-task; gradient surgery is over-engineering. Pre-filter + soft penalty give three layers of clear responsibility, audit-able." Switches to PCGrad **if** routing 4+ heads with measurable negative transfer appears.

## 2. Reranker: MMR  vs  DPP

**I pick (the most important architectural trade-off of the question)** MMR with hard quota across 3 axes.

| Dim                | MMR (pick)                                            | DPP                                            |
|--------------------|-------------------------------------------------------|------------------------------------------------|
| List size fit      | **n=3 perfect** -- short list, MMR is enough          | n>=10 to show kernel power                     |
| Implementation     | Greedy, deterministic                                 | Determinant compute, learned kernel optional   |
| Tunability         | lambda parameter + 3 axes (commenter / sentiment / topic) | Learned kernel hard to audit                  |
| Future upgrade     | -> DPP **when list expands to top-10+**               | -                                              |

**Why pick**: "For n=3, MMR with hard quota (no 2 same commenter, <=1 OP self-reply) gives me a deterministic diversity guarantee with auditable knobs. DPP at n=3 is solving for n=20 with n=3 evidence." Switches to DPP **if** the surface grows to top-10+ pinned comments.

## 3. Negative sampling: 'unexposed = negative'  vs  IPS + bandit backfill

**I pick (the question's core difficulty -- selection bias ML solution)** IPS-weighted exposed-not-engaged + unexposed-as-unknown + 5% bandit exploration backfill.

| Approach                          | Why                                                              |
|-----------------------------------|------------------------------------------------------------------|
| **IPS + bandit (pick)**           | Theoretically correct; catches under-exposed long tail; 5% bandit is an explicit budget |
| Unexposed = negative              | **Massive false negatives** -- the worst manifestation of selection bias |
| Pure random exploration           | UX degradation too large                                         |

**Switching trigger**: "If the 5% bandit budget gives 0 net-new positives after 4 weeks -> raise to 8%; if commenter-complaint rate rises -> lower to 3% with a quality-eligibility filter."

## 4. Label level: L3 engagement-to-impression ratio  vs  L1 binary  vs  L4 multi-task

**I pick** L3 (rolling-window ratio in [T, T+1h]).

**Why pick**: "L3 adds one step over L2 -- normalize by impression count. That step divides out the impression advantage a high-position comment gets, front-loading partial debias to the label layer one defensive layer ahead of the model-level bias tower. L4 multi-task is left for senior follow-up." Switches to L4 **if** head-weighting design becomes the senior follow-up direction.

## 5. Bias handling: shallow bias tower + mask  vs  feature input  vs  IPS only

**I pick** shallow bias tower with mask-at-inference (YouTube 2019).

| Dim              | Bias Tower (pick)              | Feature-into-main-tower      | IPS only                       |
|------------------|--------------------------------|------------------------------|--------------------------------|
| Decomposition    | Additively separable           | Content x position entangled | Training-time correction only  |
| Inference mask   | Well-defined                   | OOD, representation polluted | N/A (no mask)                  |
| Gradient share   | Main tower learns relevance    | Position steals gradient     | N/A                            |

**Why pick**: "**Bias tower + mask is an architectural mechanism; IPS is a statistical correction. They are not in conflict -- but the bias tower is first-line defense, IPS is second-line.**" Switches to feature-input **if and only if** position becomes truly random (e.g., experimental shuffling) -- then theoretical equivalence holds.

## 6. Train/eval split: time-based + user holdout  vs  random

**I pick** time-based primary + user-level holdout secondary.

**Why pick**: "Comment ranking is freshness-sensitive -- random split leaks future popularity trend, AUC is inflated. Time-based primary is mandatory; user holdout secondary catches 'model memorizes specific users instead of learning preferences'." Switches to random **only if** the use case stops being temporal (not our regime).

## 7. Abuse model: independent  vs  shared weights with ranker

**I pick** independent abuse model (NSFW + relevance + high-risk), **NOT shared weights** with the ranker.

| Dim              | Independent (pick)                                    | Shared weights                          |
|------------------|-------------------------------------------------------|------------------------------------------|
| Risk             | Ranker cannot learn abuse pattern; no collusion       | Ranker may internalize abuse signal as engagement proxy |
| Update cadence   | Abuse model **weekly retrain** (adversarial drift)    | Coupled to ranker retrain cycle (daily) |
| Audit            | Independent precision/recall, daily monitor           | Mixed inside multi-task metric          |

**Why pick**: "Adversarial drift speed != ranker drift speed; independent model + independent retrain schedule is mandatory." Switches to shared weights **only if** abuse becomes a labeling artifact rather than adversarial -- which is not the regime here.

## 8. Loss weighting strategy: biz-context locked  vs  uncertainty weighting

**I pick** biz-context locked (comment lift value + risk budget), **NOT uncertainty weighting**.

**Why pick**: "**Loss weights are a product decision, not a statistical estimate.** Uncertainty weighting solves statistical mismatch; biz-context locking reflects product priority. The E5 boundary signal is knowing when an ML decision should defer to product." Switches to uncertainty weighting **only if** product priority is truly ambiguous and the head distribution is statistically dominant.
"""


DEFENSE = """\
# Strong Moments -- 4 verbatim English lines (say them as-is)

The 4 lines below are canonical Strong Moment shape, **internalized verbatim** -- do not explain / paraphrase / shrink. Drop them precisely at the 0-1 / 8-12 / 15-21 / 31-35 minute slots. Strong-Moment methodology (reframe-claim-3-actions-tradeoff template, 元结构, 8 meta-rules) lives in `cd://96` §3 / §5 / §6; this column carries only the speak-aloud English plus the monitoring / A/B / loop-closure wrap.

## Decision summary (which Strong Moment to fire when)

**I pick** the 4 Strong Moment slots at the 4 sections where Top-3 Comments diverges most: framing (3 twists), label (selection bias), architecture (bias tower + MMR-vs-DPP), monitoring (4 leading-vs-lagging signals). Each block has Cue + verbatim. The **unique angle** is each Strong Moment ends with a trade-off, **this is where** E5 separates from a brain dump. Latency context: p99 < 200 ms, 100x viral peak.

---

## Strong Moment #1 -- 3 Unique Twists Framing (0-1 min, opening)

**Cue**: declarative open "Scope: ... viewer-primary set-selection, retrieval bounded ... let me put 3 twists on the table".

> "**Three unique twists vs generic ranking, each with a design implication**.
>
> **First, comment is not a generic item** -- ultra-short text, authorship is a user-graph node, social signal is dominant. Implication: text + social fused representation, commenter as a sub-entity in the main tower.
>
> **Second, early-comment time-bias** -- comments posted in the first minutes accumulate disproportionate impressions, so raw counts confound arrival time with quality. Implication: engagement velocity, a rate-not-count feature, plus a bandit exploration budget for late comments.
>
> **Third, community health as guardrail, not as a head** -- toxicity is disqualifying, not 'less engagement'. Implication: independent abuse model + toxicity hard filter pre-ranker. Treating compliance as a soft loss term is a category error.
>
> Time plan: 15 minutes framing / metric / label / feature, 25 minutes model / serving / monitoring. Does that anchor make sense, or is there a different angle you'd like me to start from?"

---

## Strong Moment #2 -- Selection Bias 3-Stage Negative Label (8-12 min, label section)

**Cue**: after announcing 'Negative label is the core difficulty of this question', "**Let me walk through the three-stage negative label**". This is where the selection-bias twist pays off versus a generic CTR ranker.

> "**Negative label is the core difficulty here, because of selection bias on the comments we never showed**.
>
> **Explicit negatives** -- dislike, report -- are strong signals; we use them directly.
>
> **Exposed-not-engaged** are standard negatives, but I IPS-weight them by propensity from a separate logging-policy model so that low-propensity items get higher sample weight at training -- a counterfactual correction.
>
> **Unexposed** is where naive systems break: if you label every unexposed comment as negative, you teach the model that good things are bad whenever retrieval missed them. So I treat unexposed as **unknown** and backfill with a **5% per-session bandit exploration budget**, which gives unbiased label on the under-exposed long tail.
>
> **Hard negative mining from the previous model** -- high-prediction-but-no-engagement items -- teaches the model to discriminate confidence-high mistakes.
>
> Why this matters more than IPS alone: IPS corrects bias in the data you have; the bandit changes the data you collect. **It is a stronger lever, but it requires cross-functional cost** -- product and growth pay part of the bill that ML would otherwise pay in accuracy loss."

---

## Strong Moment #3 -- Bias Tower + MMR vs DPP (15-21 min, architecture section)

**Cue**: after introducing the L2 ranker structure, "**Let me unpack two decisions inside this -- the bias tower, and MMR vs DPP**". This is the most important architectural trade-off in the question.

> "**The first architectural decision is the bias tower**. I add a **shallow additive bias tower** -- linear or 1-2 layers -- whose input is **bias features only**: position, popularity, recency, device, slot type. Output is added to the main-tower logit at training. At inference, the **bias term is zeroed entirely**. Companion trick: position-feature dropout in training to make the model robust to missingness.
>
> Why a separate tower rather than putting position into the main tower: the shallow inductive bias **cannot absorb content signal**, so it leaves room only for additive bias and the main tower is forced to learn real relevance. Mixing position into the main tower entangles content with position, contaminates the inference distribution, and makes position steal gradient share from real features. The bias tower is **additively separable**, so masking is well-defined.
>
> **The second architectural decision is reranking with MMR, not DPP**. For n=3 the list is too short for DPP's set-level optimization -- the 3-item determinant is dominated by any pairwise cosine, costing DPP its theoretical edge. **I pick MMR across 3 axes -- commenter, sentiment, topic -- plus a hard quota** (no two same-commenter items, at most one OP self-reply). **Switches to DPP with a learned kernel when the list expands to top-10+** -- not 'MMR is better', but 'MMR for this regime, DPP if regime changes'."

**Bonus closer (objective combination, said immediately after the architecture claim)**:

> "On objectives, I combine three: engagement (multi-head), set-level diversity, and compliance / safety. Combination strategy: multi-task heads for engagement and diversity, but **compliance applied as a hard filter pre-ranker, not a loss term** -- compliance violations are not 'less engagement', they are disqualifying. **Treating them as a soft loss term is a category error** recommendation teams often make."

---

## Strong Moment #4 -- 4 Monitoring Signals + List-level A/B (31-35 min, monitoring section)

**Cue**: actively opening, "**Let me zoom out from the model and talk about monitoring, A/B, and the abuse loop -- because these decide whether the design ships safely**". This is the E5 boundary signal -- the wrap-up Strong Moment.

> "**Model health monitoring needs four signals, ordered by leading vs lagging**.
>
> **Signal 1, online-offline metric gap**: eval AUC vs online CTR divergence > X% -- an early signal of label leak or distribution shift.
>
> **Signal 2, prediction distribution shift**: KL divergence of model output day-over-day. This is **earlier than metric degradation**, so it is the leading-est indicator. Most candidates only say 'monitor AUC'; this is the senior signal.
>
> **Signal 3, feature drift**: PSI on top features, hourly.
>
> **Signal 4, engagement metric**: 24h moving average vs baseline. Lagging -- by the time it drops users have churned.
>
> **A/B for top-3 list-level**: user-level randomization so weekly-return metrics are consistent per user. **Primary metric is any-engagement rate in the top 3, not single-item NDCG / MRR**, because this is a set-selection problem, not pure ranking. Ramp 1% -> 5% -> 20% -> 50%, with **automatic halt when any guardrail breaches** -- circuit breaker, not manual review. **North-star** (weekly return) measured by a **4-week long-horizon holdout group**; A/B ramp decisions accept proxy-based -- we cannot wait 4 weeks per launch, but we retain the holdout for retrospective validation.
>
> **Abuse detection is an independent model** -- NSFW + relevance + high-risk -- **not shared weights with the ranker**. Adversarial drift speed != ranker drift speed; abuse model **weekly retrain**, daily precision/recall monitor. Tiered action: **hard filter** at confident, **hard demote** at uncertain -- avoids a one-size-fits-all false-positive sweep.
>
> Loop closure: monitoring outputs feed back into two places -- **training data quality** (alerts trigger sample re-labeling and hard-neg mining) and **abuse-model retraining schedule** (drift signal escalates weekly -> daily emergency). **Monitoring outputs are the input to the next iteration**, not deploy-and-forget.
>
> Are there parts of the design you'd like me to deepen?"
"""


VERBAL_OUTLINE = """\
# Top-3-Comments-specific verbal anchors (methodology lives in cd://96)

The general verbal scaffolding (declarative openers, sub-structure announce, drift recovery, ML-native YES/NO vocab table, hand-off / collaborative-mode 句式, quantification 句式, production-scar 句式) lives in `cd://96` §5 (Framing/Body/Strong/Zoom 元结构) and §6 (8 偏好节奏 meta-rules). The lines below are the only ones unique to **Top-3 Comments under a Post** -- quote them verbatim, do NOT duplicate cd96.

## 4 Strong Moment entry phrases (memorize verbatim -- these are the cue lines)

1. "**Three unique twists vs generic ranking, each with a design implication**..."  (3-twist framing, 0-1 min -- Twist 1/2/3)
2. "**Negative label is the core difficulty here, because of selection bias on the comments we never showed**..."  (label, 8-12 min -- selection-bias twist)
3. "**The first architectural decision is the bias tower** ... **The second architectural decision is reranking with MMR, not DPP**..."  (architecture, 15-21 min -- bias-tower + MMR-vs-DPP twist)
4. "**Model health monitoring needs four signals, ordered by leading vs lagging**..."  (monitoring + A/B + abuse, 31-35 min -- E5 wrap-up twist)

## Top-3-Comments-specific drift-recovery lines (NOT in cd96 -- these name Top-3 by surface)

- Drift to generic ranking -> "**Let me return to the ML core** -- for Top-3 Comments the more important question is the set-selection list-level constraint, not generic point-wise ranking."
- Asked about retrieval depth -> "**Retrieval is trivially bounded by the post's own comment pool** for this surface -- I'll spend the budget on ranker + reranker instead."
- Asked about cold-start too early -> "**Let me park cold-start until the bandit-exploration section** -- the 5% per-session budget is where that answer lives. Flag it as a known risk for now."
- Asked about QPS at framing -> "**100M DAU and 100x viral peak** -- I will come back to the serving constraint at Section 5.3; the ML decisions here do not change with QPS, only the cache TTL and prefetch concurrency do."

## Top-3-Comments-only hand-off prompt (the deepen-which-side question)

> "Want me to **deepen the label-selection-bias 3-stage design, the bias tower x MMR architectural pair, or the 4 monitoring signals + list-level A/B**?"

The 3-way choice maps to Top-3-Comments-specific levers: labels = IPS + 5% bandit + hard-neg mining; architecture = shallow additive bias tower + MMR with hard quota across 3 axes; monitoring = 4 leading-vs-lagging signals + circuit-breaker A/B + independent abuse model. Avoid offering a 4th choice -- three is the canonical Top-3 Comments carve-up.
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
    """Run AC1-AC7 + T-P0-868 schema checks (R-DRAWER, R-FORBID-*, 3-rule)."""
    import re

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

    if disp_order != DISPLAY_ORDER:
        errs.append(f"AC4 FAIL: display_order={disp_order}, expected {DISPLAY_ORDER}")

    if ANCHOR_FR_NODE not in (architecture or ""):
        errs.append("AC5 FAIL: anchor fr-node path not in architecture col")
    if ANCHOR_FR_NODE not in (prod_cons or ""):
        errs.append("AC6 FAIL: anchor fr-node path not in production_constraints col")

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

    # ----- T-P0-868 schema checks (schemas/meta_mlsd_canonical.yaml) -----
    # R-DRAWER-no-sd-drawer: no drawer table at top of any sd-golden body.
    drawer_top_re = re.compile(r"^\|.*sd://.*\|", re.MULTILINE)
    for k, v in prose_cols.items():
        if v and drawer_top_re.search(v[:2000] or ""):
            errs.append(
                f"R-DRAWER-no-sd-drawer FAIL: {k} top has '| ... sd:// ... |' table"
            )

    # R-FORBID-rhythm-philosophy: 整体节奏哲学 must not appear in overview.
    if overview and "整体节奏哲学" in overview:
        errs.append(
            "R-FORBID-rhythm-philosophy FAIL: overview still contains 整体节奏哲学"
        )

    # R-FORBID-why-this-is-strong: 'why this is strong' must not appear in defense.
    if defense and re.search(r"(?i)why this is strong", defense):
        errs.append(
            "R-FORBID-why-this-is-strong FAIL: defense still contains 'Why this is strong'"
        )

    # R-FORBID-drawer-header-literal: '| Doc | ... sd://' must not appear anywhere.
    drawer_header_re = re.compile(r"^\|\s*Doc\s*\|.*sd://", re.MULTILINE)
    for k, v in prose_cols.items():
        if v and drawer_header_re.search(v):
            errs.append(
                f"R-FORBID-drawer-header-literal FAIL: {k} contains '| Doc | ... sd://' header"
            )

    # 3-rule (section-level, at_least_one_bullet pass) for apply_3rule=true cols.
    rule_patterns = {
        "R-3RULE-decision": [
            r"\b(I pick|we pick|I choose|we choose|default to|pick A)\b",
            r"(?i)\bdecision\b.*\bover\b",
        ],
        "R-3RULE-tradeoff": [
            r"(?i)\b(costs?|at the cost of|switches? to|in exchange for)\b",
            r"\bvs\b",
        ],
        "R-3RULE-scale-sla": [
            r"\b\d+\s*(ms|µs|us|qps|QPS|dim|k|K|M|B|fps|min|sec|s)\b",
            r"\bp(50|95|99|999)\b",
            r"\bHNSW\b|\bIVF\b|\bScaNN\b|\bMMR\b|\bDPP\b",
        ],
        "R-3RULE-twist-callback": [
            r"(?i)\b(twist|unique angle|the core decision here is|this is where)\b",
            r"(?i)\bcallback (to|of)\b",
        ],
    }
    apply_3rule_cols = (
        "overview", "architecture", "dataflow",
        "production_constraints", "tradeoffs", "defense",
    )
    for col in apply_3rule_cols:
        body = prose_cols.get(col) or ""
        for rule_id, patterns in rule_patterns.items():
            hit = any(re.search(p, body) for p in patterns)
            if not hit:
                errs.append(
                    f"{rule_id} FAIL: section {col} has no matching bullet "
                    f"(at_least_one_bullet pass)"
                )

    # sd_golden.overview target_chars [1500, 4500]; defense [2500, 8500];
    # architecture [2000, 6000]; dataflow [2500, 9000].
    field_char_ranges = {
        "overview":     (1500, 4500),
        "architecture": (2000, 6000),
        "dataflow":     (2500, 9000),
        "defense":      (2500, 8500),
    }
    for col, (lo, hi) in field_char_ranges.items():
        n = len(prose_cols.get(col) or "")
        if not (lo <= n <= hi):
            errs.append(
                f"SCHEMA-charrange FAIL: {col} chars={n} not in [{lo}, {hi}]"
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
