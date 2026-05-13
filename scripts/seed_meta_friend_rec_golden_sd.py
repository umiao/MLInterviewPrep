"""Seed: T-P0-870 [Meta-MLSD] Friend Recommendation Golden -> system_designs.

INSERTs (or idempotently updates) the canonical Meta MLSD Friend Recommendation
golden example as ``system_designs(slug='meta-friend-rec-golden')``,
drawer-reachable via ``sd://meta-friend-rec-golden``. This is a **bilateral
matching** golden -- sibling of ``sd://meta-reels-golden`` (RecSys),
``sd://meta-top3-comments-golden`` (list-level), and
``sd://meta-weapon-ads-golden`` (T&S classification). Cross-link via cd://96
§1/§3 drawers (added by T-P0-871).

Per schemas/meta_mlsd_canonical.yaml (rule R-NARRATIVE-prose-form, added
2026-05-13): sd-golden docs are now English oral-recital narrative scripts,
NOT bullet-heavy markdown notes. Each section opens with a declarative
one-sentence claim, runs bold-anchored substantive prose, and closes with a
trade-off / handoff sentence. >=3 **bold** spans per apply_3rule section;
<=4 consecutive bullets; <=3-row tables; first-person 'I' voice. Friend-rec
is the highest-risk doc for falling back into bullet form because the source
attachment is the most table-heavy.

4 unique twists (the question's senior signal vs generic recommendation):

  1. Bilateral matching P(send) x P(accept) -- the optimization target is a
     PRODUCT of two asymmetric distributions, not a single P(click). Sender
     intent and receiver receptivity are different physical signals that
     route through different gating heads in MMoE. Implication: MMoE
     multi-head bilateral, where the bottom is shared and each gate routes
     one expert subset to P(send), another to P(accept).
  2. Network-effect counterfactual -- treatment effect leaks across friend
     edges, so user-level randomization contaminates both arms. Implication:
     cluster-randomized A/B at community-detection clusters, with a
     SUTVA-violation check as part of the experimental contract.
  3. NRT bilateral signal -- friend graphs change in seconds (acceptance,
     rejection, recent block), and both sides' state matters at score time.
     A daily snapshot misses 90%+ of the action. Implication: a
     near-real-time signal lane that fuses sender-side AND receiver-side
     events into the model at score time, not a batch feature.
  4. Two-sided feed quality + abuse posture as upstream constraint --
     spammers maximize P(send), abuse-victims minimize P(accept-from-
     stranger), and the platform abuse posture must filter before ranking.
     Implication: an abuse-aware admission gate before retrieval, plus
     per-relationship-type calibration so growth thresholds compose with
     safety thresholds on the same probability scale.

Key content anchors (from task description T-P0-870 + canonical YAML
R-90S-friend-rec-section5):

  - MMoE multi-head bilateral: shared bottom, two gating heads (one for
    P(send), one for P(accept)) feeding two task-specific towers; combined
    via P(send) * P(accept) at serving with per-relationship-type
    calibration.
  - Cluster-randomized A/B: SUTVA violation under user-level randomization;
    cluster the social graph via Louvain / Leiden community detection and
    randomize at cluster level. Variance recovery via leave-one-cluster-out
    delta method.
  - NRT bilateral signal: dual-sided streaming join (Kafka -> Flink) on
    last-N seconds of accept/reject/block events; latency budget 60s
    end-to-end; serves into the model at score time as a state feature.
  - 5 retrieval channels (compressed to one narrative paragraph): mutual
    friends, 2-hop graph, embedding-similarity (two-tower), cohort overlap,
    inferred-real-life (org/school/contacts). Each channel feeds a candidate
    pool; ranker fuses across channels at top-K.
  - Model ladder LR -> XGBoost -> DNN -> MMoE -> Transformer compressed to
    one paragraph: each step justified by a specific failure mode of the
    prior; Transformer is the future tense (not yet the deployed default).

Section 5 (the dataflow section's model+serving section, 15-20 min slot) is
the highest-risk fall-back-to-encyclopedia surface; the R-90S forcing
function 'if only 90 seconds, which 3 sentences?' applied here yields MMoE
multi-head bilateral + cluster-randomized A/B + NRT bilateral signal as
the L4+ moments.

Architecture and production_constraints both embed a short anchor sentence
pointing to fr-node ``meta-prep/system-design-must-knows/mmoe-ple-multitask``
(id=258) for the deep-version MMoE-multi-task walkthrough; the deep version
is owned by a separate fr-node task.

Idempotent: re-running upserts in place by `slug`. Sentinel-based UPSERT keyed
on `slug='meta-friend-rec-golden'`.

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
    "Meta MLSD Golden Example -- canonical 4-twist bilateral-matching framing "
    "(P(send) x P(accept) MMoE multi-head / cluster-randomized A/B / "
    "NRT bilateral signal / abuse-posture admission) + MMoE multi-head ranker "
    "behind a 5-channel retrieval funnel. Adjacent to sd://meta-reels-golden, "
    "sd://meta-top3-comments-golden, and sd://meta-weapon-ads-golden; "
    "cross-link via cd://96 §1 timing skeleton + §3 Strong Moments drawer."
)
DISPLAY_ORDER = 133
SOURCE_PATH = (
    "docs/prep/meta_mlsd_2026-05-13_friend_rec/"
    "source_07_friend_recommendation_rewritten.md"
)

ANCHOR_FR_NODE = "meta-prep/system-design-must-knows/mmoe-ple-multitask"


OVERVIEW = """\
# Friend Recommendation -- 45min Golden Walkthrough

**I'd reframe this as a bilateral matching problem with P(send) x P(accept) as the optimization target, not a single P(click) ranker**, and that reframe is where the senior signal lives. The model serves a **two-sided platform decision** -- show user A a candidate B such that A is likely to send AND B is likely to accept -- because optimizing only sender-side intent floods receivers with unwanted requests and degrades the platform. The unique angle: **four intrinsic twists** -- bilateral matching as a product of two asymmetric distributions, network-effect counterfactual contamination, NRT bilateral signal as a serving-time state feature, and abuse-posture as an upstream admission constraint -- drive almost every downstream decision. Methodology (timing skeleton, vocab YES/NO, 8 rhythm meta-rules, E4/E5 boundary) lives in `cd://96`; this row owns only the solution.

## Twist 1 -- Bilateral matching P(send) x P(accept)

A friend recommendation is a **two-sided handshake**, not a one-sided click. **I pick** **MMoE multi-head bilateral**, where the shared bottom feeds two gating heads -- one routes a subset of experts to a P(send) tower, the other to a P(accept) tower -- and the serving score is the product `P(send) * P(accept)` with per-relationship-type temperature scaling. **Costs**: two task heads, two label streams, and a joint calibration table. **Switches to** a single weighted-loss ranker only if the receiver-side label collapses below volume quorum. This is where the bilateral twist of Strong Moment #3 lives.

## Twist 2 -- Network-effect counterfactual (cluster-randomized A/B)

Treatment effect leaks across friend edges -- a user in treatment sends requests to users in control, contaminating both arms. **I pick** **cluster-randomized A/B** at Louvain / Leiden communities, with variance recovered via a **leave-one-cluster-out delta method** because cluster sizes are unbalanced. **Costs**: weekly clustering refresh and ~10x larger sample sizes per cell vs user-level. **Switches to** user-level only on **post-acceptance** outcomes (where the network has already mutated) -- at the cost of treatment-effect bias on candidate-selection.

## Twist 3 -- NRT bilateral signal (both sides, score-time)

Friend graphs mutate in seconds and **both sides' recent state matters at score time**. A daily batch misses 90%+ of the recent-action surface -- a user who just rejected three requests is signaling "stop", and a daily snapshot never sees it. **I pick** an **NRT dual-sided streaming join** on the last-N seconds of accept/reject/block events for both A and B, joined into the model as a state feature at score time. **Costs**: a Kafka -> Flink lane with 60s end-to-end SLA plus dual-write to the feature store. **Switches to** daily batch only if streaming infra degrades -- at the cost of a measurable acceptance-rate drop on recent-action sub-populations.

## Twist 4 -- Two-sided feed quality + abuse-posture upstream

Spammers maximize P(send) and abuse-victims minimize P(accept-from-stranger), so the **abuse-posture filter is upstream of ranking**, not a post-hoc rerank. **I pick** an **abuse-aware admission gate** before retrieval plus **per-relationship-type calibration** so that growth thresholds compose with safety thresholds on the same probability scale. **Costs**: a 6-hour abuse-flag refresh and a per-relationship-type temperature table. **Switches to** a single global threshold only if abuse posture flattens across relationship types -- which it does not.

## 4 Strong Moment slots (pre-allocated, do NOT improvise)

The 4 slots fire at fixed times. **Slot #1 (0-1)** carries the 4-twist framing with the "bilateral matching, not a single ranker" reframe and the 15/25 time plan. **Slot #2 (8-12)** carries bilateral label schema and the disagreement on what counts as a positive (send-only vs send+accept vs sustained-engagement). **Slot #3 (15-21)** carries the MMoE multi-head bilateral architecture, the 5-channel retrieval funnel, and the NRT bilateral signal at score time. **Slot #4 (31-35)** carries cluster-randomized A/B with leave-one-cluster-out variance recovery, the SUTVA violation diagnostic, and the rollout circuit-breaker. The dataflow / defense / tradeoffs columns are the solution body; verbal_outline + cheat_sheet hold only Friend-Rec-specific anchors -- anything else (rhythm rules, vocab YES/NO, E4/E5) belongs in `cd://96`.
"""


ARCHITECTURE = """\
# Architecture: 5-Channel Retrieval Funnel + MMoE Multi-Head Bilateral + NRT Signal Lane

## Decision summary (the architectural twist)

**I pick** a **5-channel retrieval funnel into an MMoE multi-head bilateral ranker** -- mutual-friend / 2-hop / two-tower embedding / cohort / inferred-real-life -- all feeding a ranker that produces calibrated `P(send)` and `P(accept)` combined as a product at serving. **This is where** the bilateral matching twist of Strong Moment #3 lives. The **unique angle** versus a generic two-tower ranker is the MMoE multi-head split, the abuse-aware admission gate before retrieval, and the NRT bilateral signal joined at score time -- not as a batch feature. Latency: **retrieval p99 < 30 ms** across all 5 channels parallel, **ranker p99 < 50 ms**, **NRT lookup p99 < 10 ms**, **end-to-end p99 < 100 ms** for the people-you-may-know unit.

## Channel 0 -- abuse-aware admission gate (before retrieval)

**Before** any retrieval channel runs, an **admission gate** evaluates the requesting user against an **abuse-flag feature table** (known spammer outbound, known abuse-victim inbound, recent ToS-violation) and **short-circuits** the pipeline if flagged. **I pick** placing this gate upstream of retrieval, not as a post-hoc rerank, because spammer recs must never enter the candidate pool. **Costs**: 6-hour refresh on the abuse-flag table plus a per-relationship-type threshold table. **Switches to** post-hoc rerank only if abuse-flag refresh latency stalls -- already a P1 incident.

## Channel 1-5 -- the retrieval funnel (5 channels, one paragraph total)

**Compressed to one narrative paragraph (R-90S forcing function)**: the **5 channels** are mutual-friends (cheap graph adjacency, ~1k candidates), 2-hop graph (Counter-based hop-aggregation, ~5k candidates), two-tower embedding similarity (HNSW ANN at **M=32, p99 < 8 ms**, ~3k candidates), cohort overlap (shared school / employer / group, ~2k candidates), and inferred-real-life (org chart, contact-book hash join, location co-presence, ~1k candidates). Each channel emits a per-channel-scored pool; the union is **deduplicated with channel-of-origin preserved as a one-hot feature** for ranker fusion. **The core decision here is** that 5 channels in parallel is **a candidate-coverage decomposition** (each surfaces a different friend-type signal) and a **single end-to-end model would conflate all 5**.

## Ranker -- MMoE multi-head bilateral (the core, expand ~90s)

The main ranker is **MMoE** with a **shared bottom**, **two gating heads**, and **two task-specific towers**: P(send) predicts sender intent, P(accept) predicts receiver receptivity. Each gate routes a soft mixture of experts to its task tower so the experts specialize without hard partitioning. **I pick** MMoE over a single weighted-loss ranker because the two distributions are **physically asymmetric** -- sender-side signals (browse history, mutual-friend count) differ from receiver-side signals (recent-block, accept-rate-from-strangers) -- and a single weighted loss forces a compromise that under-fits both heads. **Switches to** Progressive Layered Extraction (PLE) only if the heads start interfering (negative transfer) at scale, which has not been observed at this corpus size.

The two heads are **calibrated to a shared posterior** so the product `P(send) * P(accept)` is interpretable -- not just a ranking. **Per-relationship-type temperature** scales each head separately for **stranger / colleague / school / real-life-contact** because base-rate acceptance varies by type; a global temperature over-pulls strangers and under-pulls contacts.

## NRT bilateral signal lane (score-time)

The **NRT signal lane** is a **Kafka -> Flink** streaming pipeline maintaining per-user **last-N seconds of accept/reject/block events** on both sender (A) and receiver (B) sides of every score-time lookup. The feature is **joined at score time**, not as a batch precompute, because the recent-action signal **decays in seconds** and is most informative inside 60s. End-to-end SLA: **60s** from event to model. **Switches to** daily-batch fallback only if streaming infra degrades -- with a soft alarm if NRT feature freshness exceeds 5 minutes.

==> Section-stitch: the 5 channels map back to Twist 4's two-sided abuse posture, and the MMoE multi-head delivers what Twist 1 promised on bilateral matching as a product of two distributions.

## MMoE-multi-task digest (this section self-contained -- deep version in fr-node)

**3-sentence core**:

1. **Shared bottom + per-task gating**: the bottom encodes a shared representation, and each gate produces a soft mixture over experts feeding its task tower; hard partitioning forces a tradeoff while MMoE's soft mixture lets heads borrow strength without negative transfer.
2. **Two-task calibration with shared posterior**: P(send) and P(accept) are independently temperature-scaled per relationship type so the product is a calibrated bilateral probability. **This is where** the cascade-of-scores property is preserved across the MMoE split.
3. **Negative-transfer monitor**: per-task AUC tracked separately; if one degrades while the other improves, the gate is shorting and a PLE migration is triggered.

**Deep version in fr-node `""" + ANCHOR_FR_NODE + """`** -- MMoE vs PLE vs SNR, negative-transfer theorem, third-task-head checklist. A separate fr-node task owns that 深版.

## Architectural choices -> 4 twists (callback)

The MMoE multi-head bilateral answers Twist 1 (bilateral matching as a product of distributions). The cluster-randomized A/B contract (in production_constraints) answers Twist 2 (network-effect counterfactual). The NRT signal lane answers Twist 3 (recent-action surface). The abuse-aware admission gate plus per-relationship-type calibration answers Twist 4 (abuse posture upstream). **Each architectural decision callback to a framing twist** -- this is the property the bilateral pipeline was designed for.
"""


DATAFLOW = """\
# Dataflow: 4-Section Verbatim Walkthrough (Phase 2 -- 15min framing + body)

## Decision summary (the rhythm twist)

**I pick** a chronological 4-section walk over a component-by-component walk because **the core decision here is** time-allocation: 4 Strong Moments at fixed slots (0-1 framing / 8-12 label / 15-21 architecture / 31-35 monitoring), and **this is where** E4 vs E5 wrap diverges. The walk follows the canonical body order **framing -> metric+label -> feature -> model+serving**, with scale anchors named verbatim: **billions of friend-graph edges**, **a few hundred million daily active users**, **end-to-end p99 < 100 ms** on the people-you-may-know unit, **retrieval p99 < 30 ms** across 5 channels in parallel.

## Section 1: Framing (90s)  <- Strong Moment #1

"L1 (user): **The user of this ML output is a two-sided handshake**, not a one-sided viewer. Both the requesting user (sender) and the candidate (receiver) consume the output. Optimizing only sender-side intent floods receivers and degrades the platform.

L2 (scale): **A few hundred million DAU, billions of friend-graph edges, tens of millions of PYMK impressions per day**; per-user candidate-pool **~10k after retrieval, top-K = 20**. SLA: **end-to-end p99 < 100 ms** on home-feed, **NRT freshness < 60s**, **abuse-flag refresh every 6 hours**.

L3 (twists with implications):

- **Bilateral matching P(send) x P(accept)** -> MMoE multi-head bilateral, two task heads, product at serving
- **Network-effect counterfactual** -> cluster-randomized A/B at Louvain communities, leave-one-cluster-out variance
- **NRT bilateral signal** -> dual-sided streaming join at score time, last-N-seconds state feature
- **Abuse-posture upstream** -> admission gate before retrieval, per-relationship-type calibration

L4 (ML formulation): **5-channel retrieval funnel into an MMoE multi-head bilateral ranker**, with NRT signal joined at score time and an abuse-aware admission gate upstream of retrieval. The serving score is the product `P(send) * P(accept)` -- a true bilateral probability, not just a relative ranking."

==> Section-stitch: each of these 4 twists hooks into a specific downstream metric, label rule, or serving constraint -- the next 3 sections trace exactly that.

## Section 2: Metrics and Labels (180s)  <- Strong Moment #2

"**L1 North-star is sustained-bilateral-engagement at 28 days, not raw acceptance rate**. Raw acceptance is gameable by lowering the acceptance threshold; 28-day sustained engagement (number of post-acceptance interactions -- messages, posts, reactions -- between A and B in the 28 days after acceptance) is the platform-value-aligned metric.

**L2 Proxies**, each with a one-line alignment statement:

- **P(send) calibrated on the sender** -> sender-intent fidelity, prevents under-recommending
- **P(accept) calibrated on the receiver** -> receiver-receptivity fidelity, prevents spam-like overrecommendation
- **Click-to-send conversion at the impression level** -> top-of-funnel sender engagement
- **28-day post-acceptance message rate** -> the true downstream platform-value signal

**Label schema (the core difficulty -- this section's senior signal)**: the question of what counts as a positive is itself a senior judgment. **I pick** a **bilateral positive: send AND accept AND >=1 post-acceptance interaction in 28 days** -- this filters out one-sided fake-positives (spammer sends + reluctant accept) and zero-engagement matches (accept-then-ignore). **Costs**: a 28-day delay before label maturity, mitigated with **eligible-label fast-track** for recent items that have already crossed both send AND accept (counted as provisional positives with a sample-weight reduction).

**Negative sampling (asymmetric)**: random negatives **vs** hard negatives drawn from the impressed-but-not-clicked pool. **I pick** a **70/30 random/hard split** for the P(send) head and a **50/50 split** for the P(accept) head, because the P(accept) head needs the harder negatives to learn the receiver-side decision boundary; the P(send) head benefits from broader random negatives to keep the retrieval recall high. **Switches to** uniform random negatives only if the hard-negative pool collapses below volume.

**Three-eval-set discipline (analogous to T&S, but tuned to bilateral)**:

- **Frozen golden set** on a 4-week-old slice -- 'does the model meet a fixed bilateral-engagement bar?' -- never updated.
- **Rolling weekly set** -- 'how is the model doing on this week's traffic?' -- refreshed every Monday from the prior week's matured-label sample.
- **Cluster-randomized counterfactual set** -- 'is the cluster A/B counterfactual estimate trending consistently?' -- continuously updated with live experimental clusters.

**Do NOT collapse these to one eval-set** -- each answers a different question."

==> Section-stitch: the bilateral positive defines the two heads (P(send) + P(accept)) that the architecture in Section 4 will need.

## Section 3: Features (60s) -- 4-quadrant model

"**4-quadrant model, but the heaviest quadrant is interaction-side (sender x receiver pair)**:

**Sender (user A)**:

- Friend graph degree + recent friend-add velocity (sender-intent signal)
- Browse history + people-you-may-know dwell time + recent profile-views
- Recent send-reject ratio (de-prioritize chronic spammers)

**Receiver (user B)**:

- Friend graph degree + accept rate from strangers (receiver-receptivity signal)
- Recent block / report behavior (abuse-victim signal)
- Inbox depth (overloaded receivers under-accept regardless of fit)

**Interaction (the heaviest quadrant -- this is where the bilateral twist lives)**:

- **Mutual-friend count** + **Adamic-Adar weight** (cheap, the L3 carve-up anchor from the cd://96 hub)
- **Channel-of-origin** as a one-hot feature (mutual / 2-hop / embedding / cohort / inferred-real-life)
- **Cohort overlap depth** -- shared school, employer, group memberships
- **Inferred-real-life signal** -- org chart, contact-book hash join, location co-presence

**Context**:

- Recent friend-rec impression density (avoid showing the same candidate too often)
- Surface (home feed PYMK unit vs notifications-tab vs onboarding flow)

**Critical distinction**: the **NRT lane** carries **state features**, not aggregations -- last-N-seconds accept/reject/block events on both sides, joined at score time. This is the root of why a daily-batch-only feature set is insufficient -- without the NRT lane, a user who just rejected three requests gets re-recommended to similar candidates within the same hour."

==> Section-stitch: the 5 retrieval channels feed the channel-of-origin one-hot in the ranker; the NRT signal lane joins at score time on both sides.

## Section 4: Model and serving (60s) -- Strong Moment #3 land here

"**The ranker is MMoE multi-head bilateral**: shared bottom encoder, two gating heads (one per task), two task-specific towers (P(send) and P(accept)), with the serving score the **product** `P(send) * P(accept)` calibrated per relationship type.

**Model ladder (R-90S compression -- one paragraph)**: the deployment lineage is **LR -> XGBoost -> DNN -> MMoE -> Transformer**; each step is justified by a specific failure of the prior -- LR fails on feature crosses, XGBoost fails on embedding co-training, DNN fails on bilateral asymmetry under a single weighted loss, MMoE captures the bilateral via per-task gates, and Transformer is the next-tense option for **sequence-aware bilateral signal**. **I pick** **MMoE as the deployed default**, not because Transformer is worse in offline AUC, but because at this scale MMoE's serving latency is **~3x cheaper at p99** and the offline AUC gap is **< 0.5%**.

**5 retrieval channels (R-90S compression -- one paragraph)**: candidate retrieval runs **5 channels in parallel** (mutual / 2-hop / two-tower-embedding / cohort / inferred-real-life), each emitting a per-channel-scored pool, deduplicated with **channel-of-origin preserved as a one-hot feature**. **HNSW M=32 p99 < 8 ms** on the two-tower channel; mutual-friend channel is **O(degree)** at p99 < 10 ms; 2-hop is **O(degree^2)** with a **6-hour cache** at p99 < 15 ms. Channels are independent so a single-channel outage degrades retrieval recall but does not fail the request.

**NRT bilateral signal**: score-time join brings **last-60s accept/reject/block on both A and B** into the ranker via a **Flink hot-key lookup** with **p99 < 10 ms** budget. Without it, recent-action is missed for ~90% of impressions.

**Latency budget**: retrieval p99 < 30 ms (5 channels parallel), ranker p99 < 50 ms, NRT p99 < 10 ms, end-to-end p99 < 100 ms. Throughput: tens of millions of impressions per day, onboarding peaks **~5x average**."

==> Section-stitch: the MMoE bilateral + NRT join + 5-channel retrieval funnel set up Section 4's production_constraints discussion on cluster-randomized A/B and the rollout circuit-breaker.
"""


FORMULAS = """\
# Bilateral Matching Score + MMoE Multi-Head Gating + Cluster-Randomized A/B (3 anchors)

## Bilateral matching score (the optimization target)

For a candidate pair (A, B) where A is the requesting user and B is the recommended candidate, the model produces two calibrated scores:

```
P(send | A -> B)    = sigmoid(z_send   / T_send[reltype(A,B)])
P(accept | A -> B)  = sigmoid(z_accept / T_accept[reltype(A,B)])
```

The serving score is the **product** of the two:

```
score(A, B) = P(send | A -> B) * P(accept | A -> B)
```

Per-relationship-type temperatures `T_send[reltype]` and `T_accept[reltype]` are calibrated separately for `stranger / colleague / school / real-life-contact`. Without per-relationship calibration, a single global temperature **over-pulls the stranger relationship type** (where base-rate acceptance is ~5%) and **under-pulls real-life-contact** (where base-rate acceptance is ~80%). The product is **a calibrated bilateral probability**, not just a ranking, which is the property that lets growth and safety thresholds compose at the policy layer.

## MMoE multi-head gating (the architectural anchor)

The MMoE bottom encodes user + candidate + interaction features into a shared representation `h` of dimension `d`. For each task `t in {send, accept}`, a softmax gate `g_t(h)` produces a mixture over `n` experts:

```
g_t(h)          = softmax(W_t * h)                # shape: (n,)
mix_t(h)        = sum_{i=1..n} g_t(h)_i * E_i(h)  # shape: (d',)
P(t | A, B)     = sigmoid(tower_t(mix_t(h)))      # task-specific scalar head
```

Each expert `E_i` is a small MLP shared across tasks; the per-task gating lets the two heads borrow strength from overlapping experts without forcing a hard partition. A **negative-transfer monitor** tracks per-task AUC drift; if `AUC_t1` degrades while `AUC_t2` improves, the gate is shorting `t1` and a PLE migration is triggered.

## Cluster-randomized A/B with leave-one-cluster-out variance

The treatment effect under SUTVA-violation is biased if randomization is at the user level. Cluster randomization at the community level recovers an unbiased estimate. For `K` clusters with assignment `Z_k in {0, 1}` and per-cluster average outcome `Y_k`:

```
TE_cluster      = (sum_k Z_k * Y_k) / (sum_k Z_k) - (sum_k (1 - Z_k) * Y_k) / (sum_k (1 - Z_k))
var_LOCO        = (K / (K - 1)) * sum_k (TE_{-k} - mean_k TE_{-k})^2
```

`TE_{-k}` is the treatment-effect estimate with cluster `k` held out. The LOCO variance recovery **costs more clusters** (variance scales with cluster count, not user count), which forces ~10x larger sample sizes than user-level randomization but recovers the unbiased counterfactual under network spillover.

## Three eval-set discipline (formal definition)

| Eval Set                | Refresh         | Answers                                              |
|-------------------------|-----------------|------------------------------------------------------|
| Frozen golden           | Never           | Does the model meet a fixed bilateral-engagement bar? |
| Rolling weekly          | Mondays         | How is the model doing on this week's mix?          |
| Cluster counterfactual  | Continuous      | Is the cluster A/B trending consistently?           |

**Each row answers a distinct question; do NOT collapse to a single eval-set** -- a model can look good on the frozen set and be silently broken on the cluster counterfactual. The senior signal is naming all three and saying when to read which.
"""


PRODUCTION_CONSTRAINTS = """\
# Production Constraints: Daily Retrain + Cluster-Randomized A/B + NRT Lane + Rollout Circuit-Breaker

## Decision summary (the production twist)

**I pick** a **daily ranker retrain** on rolling 30 days of bilateral labels, a **6-hour 2-hop cache refresh**, an **NRT bilateral signal lane** with a 60s end-to-end SLA, and a **cluster-randomized A/B contract** with leave-one-cluster-out variance recovery -- **this is where** the bilateral matching twist meets the wire. **Throughput**: tens of millions of people-you-may-know impressions per day, **onboarding-spike peaks ~5x average**, with **end-to-end p99 < 100 ms** on the home-feed PYMK unit and **NRT feature freshness < 60s**. The unique angle versus a generic recommendation deployment is the **network-effect counterfactual contract on cluster-randomized A/B**, not the model weights -- that contract is the actual change-management surface.

## Latency budget and serving topology

The 5-channel retrieval funnel runs **in parallel** at p99 < 30 ms (mutual-friend channel on the friend graph at p99 < 10 ms, 2-hop with a 6-hour cache at p99 < 15 ms, two-tower **HNSW M=32** at p99 < 8 ms, cohort at p99 < 15 ms, inferred-real-life at p99 < 20 ms). The MMoE ranker on the deduplicated ~10k-candidate pool runs at p99 < 50 ms. The NRT bilateral signal **joined at score time** on both A and B adds a Flink hot-key lookup at p99 < 10 ms. End-to-end p99 < 100 ms on the home-feed PYMK unit; without the NRT lane the recent-action signal is missed for ~90% of impressions.

## Retrain cadences (tiered, not one-size-fits-all)

| Cadence              | What                                                                              |
|----------------------|-----------------------------------------------------------------------------------|
| Streaming 6h         | 2-hop graph cache, abuse-flag refresh, per-relationship-type threshold table      |
| Daily                | MMoE ranker retrain on rolling 30 days, per-task calibration temperatures         |
| Weekly               | Two-tower embedding retrain, Louvain cluster refresh for A/B randomization        |

The NRT lane is its own streaming-60s tier, called out in prose rather than as a 4th cadence row -- accept/reject/block events older than 60s decay below signal-noise on the receiver-receptivity head. **Switches to** a 5-minute fallback only if Flink hot-key lookup latency degrades, **at the cost of** a measurable acceptance-rate drop on recent-action sub-populations.

## Cluster-randomized A/B in production (the actual change-management surface)

Friend-rec experiments **must** use **cluster-randomized A/B** at Louvain / Leiden community-detection clusters, because user-level randomization **leaks treatment effect across friend edges** and contaminates both arms. **The variance is recovered via leave-one-cluster-out** delta-method estimation; cluster sizes are unbalanced and the naive standard error underestimates the true confidence interval by 2-4x. **A SUTVA-violation diagnostic** is part of the experimental contract: if the cluster-level estimate diverges from the user-level estimate by >20%, the user-level result is rejected as biased and only the cluster result is reported. **Costs**: ~10x larger sample sizes per cell vs user-level randomization, plus a weekly clustering refresh. **Switches to** user-level randomization only on **post-acceptance** outcomes (where the network has already mutated and SUTVA is no longer violated) -- at the cost of treatment-effect bias on the candidate-selection step itself.

## Three-eval-set discipline in production

The three eval-sets each gate a different decision: the **frozen golden set** gates a calibration rotation (does the new temperature preserve the regulatory bar?), the **rolling weekly set** gates a ranker retrain release (does the retrained MMoE hold up against this week's mix?), and the **cluster-randomized counterfactual set** gates the experimental sign-off (is the trend statistically real under network spillover?). **No eval-set is a passive scoreboard** -- each one has a corresponding production action it gates.

## Rollout circuit-breaker (model + experiment)

A new MMoE ranker rolls out via **shadow scoring + 1% cluster canary -> 5% -> 25% -> 100%**, with **automatic halt** when any of three guardrails breach: P(send) head AUC degrades below baseline - 0.5%, P(accept) head AUC degrades below baseline - 0.5%, or cluster-randomized 28-day sustained-engagement metric trends below baseline - 1%. The rollout is **cluster-canary**, not user-canary, because user-canary contaminates the control arm via network spillover. **Switches to** a longer-canary 7-day cluster soak only if the negative-transfer monitor fires on either MMoE head during the canary window.

## MMoE-multi-task Production digest (self-contained -- deep version in fr-node)

The 2-piece skew defense in production is:

1. **Per-task calibration parity**: each MMoE head's calibrated P(t) is monitored daily via per-relationship-type ECE on the frozen golden set. If `ECE_t,r > 2%` for any (task, relationship-type) cell, the calibration rotation pipeline halts -- a circuit-breaker, not a manual review.
2. **Negative-transfer monitor**: per-task validation AUC is tracked separately on the rolling weekly set. If one head's AUC degrades while the other's improves by >0.5%, the gate is shorting the under-performing task and a gate-regularization or PLE migration is triggered.

**Deep version in fr-node `""" + ANCHOR_FR_NODE + """`** -- covers MMoE vs PLE vs SNR architectures, the negative-transfer theorem under task-imbalance, per-task gating regularization, and the operational checklist for adding a third task head (e.g., long-term engagement). A separate fr-node task owns that 深版.

## Production scar (E4 senior signal -- one or two sentences total)

**In my past work**, we found that an early MMoE rollout looked clean on offline AUC but degraded post-acceptance 28-day engagement; the **fix was switching from a P(send)+P(accept) sum loss to the product score with per-relationship-type calibration**, because the sum loss was masking a calibration mismatch between the two heads. **One thing we learned the hard way** is that a user-level A/B on friend-rec showed a strong positive treatment effect that **disappeared under cluster-randomization** -- the leaked treatment was contaminating the control arm through accepted requests, and the user-level estimate was biased upward by ~40%.
"""


TRADEOFFS = """\
# Tradeoffs (8 decision points -- each "I pick A because X, costs Y, switches to B if Z")

## Decision summary (the tradeoff twist)

8 tradeoffs follow, each in the form **"I pick A because X, costs Y, switches to B if Z"**. **This is where** the architectural twists meet concrete numbers: ~10k retrieval pool, top-K = 20, end-to-end p99 < 100 ms, NRT 60s SLA, daily ranker retrain, 6-hour 2-hop cache, weekly two-tower retrain + Louvain clustering refresh, per-relationship-type calibration across 4 buckets, and a cluster-randomized A/B contract.

1. **MMoE multi-head bilateral vs single weighted-loss ranker** -- I pick MMoE multi-head because the two distributions are **physically asymmetric** -- sender-side and receiver-side signals are different, and a single weighted loss forces a compromise that under-fits both heads. Costs: two task heads + per-task gating + a joint calibration table. Switches to PLE only if negative transfer emerges between the heads -- which has not been observed at this corpus size.

2. **Bilateral product P(send) x P(accept) vs sum at serving** -- I pick the product because it is a **calibrated bilateral probability**, not just a ranking, and the product **preserves the cascade-of-scores property** so growth and safety thresholds compose at the policy layer. Costs: two-task temperature scaling + per-relationship-type calibration table. Switches to a sum-of-logits ranker only if one of the two heads collapses on label volume -- **at the cost of** losing bilateral-probability interpretability.

3. **5-channel retrieval funnel vs single end-to-end retrieval** -- I pick 5 channels because each channel surfaces a different friend-type signal (mutual / 2-hop / embedding / cohort / inferred-real-life) and a single end-to-end retrieval would **conflate the 5 signals** into one loss, missing the channel-of-origin feature the ranker needs. Costs: 5 channels in parallel + dedup + a channel-of-origin one-hot. Switches to a single end-to-end retrieval **if** the channel-of-origin one-hot becomes redundant against ranker capacity, which **costs the ability to debug per-channel recall**.

4. **NRT bilateral signal at score time vs daily-batch feature** -- I pick NRT joined at score time because recent-action signal **decays in seconds** and is most informative inside the last 60s; daily batch misses 90%+ of the recent-action surface. Costs: a Kafka -> Flink streaming lane with 60s end-to-end SLA + dual-write to the feature store. Switches to daily batch only if Flink infra degrades -- with a soft alarm if NRT feature freshness exceeds 5 minutes.

5. **Cluster-randomized A/B vs user-level randomization** -- I pick cluster randomization at Louvain communities because user-level randomization **leaks treatment effect across friend edges** and biases both arms; the leak inflated a past experiment's effect by ~40%. Costs: ~10x larger sample sizes per cell + weekly clustering refresh + leave-one-cluster-out variance recovery. Switches to user-level randomization **only on post-acceptance outcomes** (where the network has already mutated and SUTVA holds), at the cost of treatment-effect bias on candidate-selection.

6. **Bilateral positive (send AND accept AND 28-day engagement) vs send-only positive** -- I pick bilateral positive because send-only is **gameable by spammers** maximizing P(send) and accept-only without engagement is **gameable by reluctant accepts**; the bilateral positive captures sustained platform value. Costs: 28-day label-maturity delay + a fast-track provisional label with sample-weight reduction. Switches to send-only **if** post-acceptance interaction labels become unobservable, which **costs the platform-value alignment**.

7. **Abuse-aware admission gate upstream of retrieval vs post-hoc rerank** -- I pick upstream admission because spammer recs must **never enter the candidate pool**; a post-hoc rerank lets them be retrieved, scored, and seen by the ranker, wasting capacity. Costs: a 6-hour abuse-flag refresh + per-relationship-type threshold table. Switches to post-hoc rerank only if the abuse-flag refresh latency stalls, which **would already be a P1 incident**.

8. **HNSW two-tower retrieval (M=32, p99 8ms) vs IVF-PQ** -- I pick HNSW because it gives **recall@100 ~95%** at p99 < 8 ms on the two-tower embedding channel, where IVF-PQ trades off recall for memory. Costs: graph memory ~2x IVF + slower index build (offline). Switches to IVF-PQ only if memory becomes the binding constraint at scale, **in exchange for** a measurable recall drop on the embedding channel.

Across all 8, the **firm-claim register** is: bilateral MMoE multi-head, P(send) x P(accept) product at serving, 5-channel retrieval funnel with channel-of-origin one-hot, NRT bilateral signal lane at score time, cluster-randomized A/B at Louvain communities, bilateral positive at 28-day engagement, abuse-aware admission gate upstream of retrieval, and HNSW M=32 two-tower retrieval.
"""


DEFENSE = """\
# Strong Moments -- 4 verbatim English lines (say them as-is)

The 4 lines below are canonical Strong Moment shape, **internalized verbatim**. Drop them at 0-1 / 8-12 / 15-21 / 31-35 minute slots. Strong-Moment methodology lives in `cd://96` §3 / §5 / §6; this column carries only the speak-aloud English plus the close-out trade-off.

## Decision summary (which Strong Moment to fire when)

**I pick** the 4 Strong Moment slots at the 4 places where Friend Rec diverges most: framing (4 twists + bilateral reframe), label (bilateral positive + asymmetric negatives), architecture (MMoE multi-head + 5 channels + NRT signal), monitoring (cluster-randomized A/B + SUTVA diagnostic + circuit-breaker). Each block follows Cue + verbatim + close-out trade-off. The **unique angle** is each Strong Moment **ends with a trade-off**, **this is where** E5 separates from a brain dump. Scale: **end-to-end p99 < 100 ms**, **NRT freshness < 60s**, **~10k candidate pool**, **top-K = 20**, **HNSW M=32**, **6-hour 2-hop cache**, **daily ranker retrain**.

---

## Strong Moment #1 -- Bilateral-Matching Reframe + 4 Twists (0-1 min, opening)

**Cue**: declarative open "**I'd reframe this as a bilateral matching problem with P(send) x P(accept) as the optimization target, not a single P(click) ranker** ... four twists."

> "**I'd reframe this as a bilateral matching problem with P(send) x P(accept) as the optimization target, not a single P(click) ranker**. The model serves a two-sided handshake -- both the requesting user and the recommended candidate consume the output -- and optimizing only sender-side intent floods receivers and degrades the platform.
>
> **Four unique twists vs generic recommendation, each with a design implication**.
>
> **First, bilateral matching is a product of two asymmetric distributions** -- sender P(send) and receiver P(accept) are physically different signals. Implication: MMoE multi-head with the serving score as the product, per-relationship-type calibrated.
>
> **Second, network-effect counterfactual** -- friend edges leak treatment effect; a past user-level A/B was biased upward by ~40% by spillover. Implication: cluster-randomized A/B at Louvain communities with leave-one-cluster-out variance.
>
> **Third, NRT bilateral signal is a state feature at score time** -- recent accept/reject/block events decay in seconds; a daily snapshot misses 90%+ of the surface. Implication: Kafka -> Flink streaming lane with 60s end-to-end SLA, joined at score time on both sides.
>
> **Fourth, abuse-posture is upstream of ranking** -- spammers maximize P(send) and abuse-victims minimize P(accept); the admission gate must filter before retrieval. Implication: abuse-aware admission gate + per-relationship-type calibration on the same scale.
>
> Time plan: **15 / 25 min split**."

---

## Strong Moment #2 -- Bilateral Label + Asymmetric Negatives (8-12 min)

**Cue**: "**Let me walk through the bilateral label and the asymmetric negative-sampling for the two heads**".

> "**The label is the core difficulty here, because what counts as a positive is itself a senior judgment** -- send-only is gameable by spammers, accept-without-engagement is gameable by reluctant accepts.
>
> **I pick a bilateral positive: send AND accept AND >=1 post-acceptance interaction in 28 days** -- this filters one-sided fake-positives and zero-engagement matches. The 28-day maturity is the platform-value signal; the cost is label delay, mitigated with an **eligible-label fast-track** counting send+accept items as provisional positives with sample-weight reduction.
>
> **Negative sampling is asymmetric**. P(send) sees a **70/30 random/hard split** because the sender boundary is broad and benefits from random negatives. P(accept) sees a **50/50 split** because the receiver decision is harder and needs impressed-but-not-clicked hard negatives. **A single uniform rate forces a compromise** that under-fits one head.
>
> **Three eval-sets gate three decisions**: frozen golden gates calibration rotations, rolling weekly gates ranker retrain releases, cluster-randomized counterfactual gates experimental sign-off. **Each has a corresponding production action**.
>
> Trade-off: bilateral positive **costs a 28-day label-maturity delay** in exchange for platform-value alignment -- the alternative is a fast but gameable signal."

---

## Strong Moment #3 -- MMoE Multi-Head Bilateral + 5 Channels + NRT Signal (15-21 min)

**Cue**: "**Let me unpack three architectural decisions -- the MMoE bilateral ranker, the 5-channel retrieval funnel, and the NRT signal at score time**".

> "**The first architectural decision is the MMoE multi-head bilateral ranker**. The shared bottom encodes user + candidate + interaction features; two gating heads produce soft mixtures over experts feeding two task-specific towers -- P(send) and P(accept). The serving score is **the product** of the two, calibrated per relationship type across stranger / colleague / school / real-life-contact.
>
> **MMoE over a single weighted-loss ranker**, because sender and receiver signals are physically asymmetric and a single weighted loss under-fits both heads. Switches to PLE only if negative transfer emerges.
>
> **The second architectural decision is the 5-channel retrieval funnel**: mutual-friend, 2-hop with 6-hour cache, two-tower HNSW at **M=32 p99 < 8 ms**, cohort overlap, inferred-real-life. Each channel emits a per-channel-scored pool, deduplicated with **channel-of-origin preserved as a one-hot feature** for ranker fusion. A single end-to-end retrieval would conflate the 5 signals; the per-channel funnel keeps signal types distinct and lets per-channel recall be debugged independently.
>
> **The third architectural decision is the NRT bilateral signal at score time**, not a batch precompute. A Kafka -> Flink streaming lane carries last-60s accept/reject/block events on both A and B, joined at score time as a state feature with **p99 < 10 ms** on the Flink hot-key lookup. Without it, recent-action is missed for ~90% of impressions."

**Bonus closer (objective combination)**:

> "Two heads: P(send) with BCE on the sender label + 70/30 random/hard negatives, P(accept) on the receiver label + 50/50 split. **The product is calibrated, not just ranked**, so growth and safety thresholds compose. **Treating bilateral matching as a single weighted-loss task is a category error**."

---

## Strong Moment #4 -- Cluster-Randomized A/B + SUTVA Diagnostic + Circuit-Breaker Rollout (31-35 min)

**Cue**: "**Let me zoom out and talk experimentation, monitoring, and rollout under network effects**". This is the E5 boundary signal.

> "**Friend-rec experiments need three things, ordered by counterfactual fidelity**.
>
> **First, cluster-randomized A/B at Louvain communities**. User-level randomization **leaks treatment effect across friend edges**; a past user-level A/B was biased upward by ~40% by spillover. Cluster A/B at Louvain / Leiden, with **leave-one-cluster-out variance** because cluster sizes are unbalanced and naive standard error underestimates by 2-4x. **Costs ~10x sample sizes** per cell, but recovers the unbiased counterfactual.
>
> **Second, SUTVA-violation diagnostic** runs alongside every cluster experiment. If the cluster estimate diverges from the user-level estimate by >20%, the user-level result is rejected and only the cluster result is reported. **This is the senior signal earlier than effect-size degradation**.
>
> **Third, online prediction-distribution drift on both heads**, hourly. KL divergence day-over-day on P(send) and P(accept) catches base-rate shifts before eval-sets do.
>
> **Rollout is cluster-canary, not user-canary**, because user-canary contaminates the control arm. A new MMoE rolls out via shadow + 1% cluster canary -> 5% -> 25% -> 100%, with **automatic halt** on three guardrails: P(send) AUC drops baseline - 0.5%, P(accept) AUC drops baseline - 0.5%, or cluster 28-day sustained-engagement trends below baseline - 1%. **Circuit breaker, not manual review**.
>
> Loop closure: monitoring feeds **the cluster-randomization plan** (weekly clustering refresh) and **the negative-transfer monitor** (gate-regularization or PLE migration on per-task AUC divergence).
>
> Trade-off: **cluster A/B costs ~10x larger sample sizes** in exchange for an unbiased counterfactual under network spillover. Want me to deepen any part?"
"""


VERBAL_OUTLINE = """\
# Friend-Rec-specific verbal anchors (methodology lives in cd://96)

The general verbal scaffolding (declarative openers, sub-structure announce, drift recovery, ML-native YES/NO vocab table, hand-off / collaborative-mode phrasing, quantification phrasing, production-scar phrasing) lives in `cd://96` §5 (Framing / Body / Strong / Zoom 元结构) and §6 (8 偏好节奏 meta-rules). The lines below are the only ones unique to **Friend Recommendation** -- quote them verbatim, do NOT duplicate cd96.

## 4 Strong Moment entry phrases (memorize verbatim -- these are the cue lines)

1. "**I'd reframe this as a bilateral matching problem with P(send) x P(accept) as the optimization target, not a single P(click) ranker** ... four unique twists vs generic recommendation, each with a design implication." (4-twist framing, 0-1 min -- Twist 1/2/3/4)

2. "**The label is the core difficulty here, because what counts as a positive is itself a senior judgment** -- send-only is gameable by spammers, accept-without-engagement is gameable by reluctant accepts." (label, 8-12 min -- bilateral positive twist)

3. "**The first architectural decision is the MMoE multi-head bilateral ranker** ... **the second is the 5-channel retrieval funnel** ... **the third is the NRT bilateral signal at score time**." (architecture, 15-21 min -- MMoE bilateral + 5 channels + NRT twist)

4. "**Friend-rec experiments need three things, ordered by counterfactual fidelity** ... cluster-randomized A/B, SUTVA-violation diagnostic, online prediction-distribution drift on both heads." (monitoring + rollout, 31-35 min -- E5 wrap-up twist)

## Friend-Rec-specific drift-recovery lines (NOT in cd96 -- these name Friend Rec by surface)

When the interviewer drifts toward generic recommendation: "**Let me return to the ML core** -- for Friend Rec the question is not the single-ranker P(click), it is the bilateral matching P(send) x P(accept) under network-effect counterfactual, because that is where the platform-value alignment actually lives."

When asked about retrieval depth: "**Retrieval is 5 channels in parallel, not a single end-to-end model** -- mutual-friend, 2-hop, two-tower embedding, cohort, inferred-real-life. The channel-of-origin is preserved as a one-hot feature so the ranker can debug per-channel recall independently."

When asked about cold-start too early: "**Let me park new-user cold-start until the inferred-real-life channel section** -- contact-book hash join plus org-chart plus location co-presence handle most new-user cold-start, and cold-start is most of the 'why a 5-channel funnel and not just two-tower' answer."

When asked about scale at framing: "**A few hundred million daily active users, billions of friend-graph edges, tens of millions of people-you-may-know impressions per day**, with onboarding-spike peaks at about 5x average. The retrieval funnel runs 5 channels in parallel at p99 < 30 ms; the MMoE ranker at p99 < 50 ms; the NRT join at p99 < 10 ms; end-to-end p99 < 100 ms. The ML decisions here do not change with QPS, only the 2-hop cache window and NRT feature freshness do."

When asked about why MMoE not Transformer: "**Transformer is the future-tense option for sequence-aware bilateral signal**, but at this scale MMoE's serving latency is ~3x cheaper at p99 and the offline AUC gap is < 0.5%. **I pick MMoE as the deployed default** and treat Transformer as the next-iteration candidate."

## Friend-Rec-only hand-off prompt (the deepen-which-side question)

> "Want me to **deepen the MMoE multi-head bilateral ranker with the per-relationship-type calibration, the 5-channel retrieval funnel with the channel-of-origin one-hot and HNSW M=32, or the cluster-randomized A/B contract with leave-one-cluster-out variance and the SUTVA-violation diagnostic**?"

The 3-way choice maps to Friend-Rec-specific levers: ranker = MMoE multi-head + two gating heads + per-relationship-type calibration + product score at serving; retrieval = 5 channels in parallel + channel-of-origin one-hot + HNSW M=32 two-tower + 6-hour 2-hop cache; experimentation = cluster-randomized A/B at Louvain + LOCO variance recovery + SUTVA-violation diagnostic + cluster-canary rollout. Avoid offering a 4th choice -- three is the canonical Friend Rec carve-up.
"""


CHEAT_SHEET = """\
# 30-sec pre-walk-in checklist -- Friend-Rec-only

Methodology (timing skeleton, 元结构, 8 meta-rules, E4/E5 boundary, drift-recovery vocab) lives in `cd://96` §1 / §5 / §6 / §8. The anchors below are Friend-Rec-specific only -- quote verbatim, do NOT overlap cd96.

## Strong Moment slot map (memorize position, anchor, twist)

| Time   | Slot    | Friend-Rec-specific anchor (the twist this slot hosts)                                          |
|--------|---------|-------------------------------------------------------------------------------------------------|
| 0-1    | **#1**  | Bilateral-matching reframe + 4 twists -- bilateral product / network-effect / NRT / abuse-posture |
| 8-12   | **#2**  | Bilateral positive label (send AND accept AND 28-day engagement) + asymmetric negatives         |
| 15-21  | **#3**  | MMoE multi-head bilateral + 5-channel retrieval funnel + NRT signal at score time               |
| 31-35  | **#4**  | Cluster-randomized A/B at Louvain + SUTVA diagnostic + cluster-canary circuit-breaker rollout   |

## Friend-Rec-only quantification anchors (drop verbatim into the appropriate moment)

- **15 / 25 min split**: 前段 framing / metric+label / feature / model+serving, 后段 production constraints + monitoring -- the Friend Rec time plan declared in the first 60s.
- **~10k candidate pool after 5-channel retrieval, top-K = 20 surfaced**: the funnel-decomposition anchor.
- **End-to-end p99 < 100 ms, retrieval p99 < 30 ms (5 channels in parallel), ranker p99 < 50 ms, NRT join p99 < 10 ms**: the 4-tier latency anchor.
- **HNSW M=32 on the two-tower embedding channel at p99 < 8 ms**: the embedding-retrieval anchor.
- **NRT 60s end-to-end SLA on bilateral signal lane**: the streaming-vs-batch anchor.
- **6-hour 2-hop cache refresh + daily ranker retrain + weekly two-tower retrain + weekly Louvain clustering refresh**: the tiered retrain cadence.
- **Cluster-randomized A/B at Louvain communities + leave-one-cluster-out variance + SUTVA-violation diagnostic + cluster-canary rollout**: the counterfactual contract.
- **A past user-level A/B was biased upward by ~40% via friend-edge spillover**: the production-scar quantification.
- **Bilateral positive at 28 days, asymmetric negatives 70/30 random/hard for P(send) and 50/50 for P(accept)**: the label-schema quantification.

## Friend-Rec-only firm-claim register (each line is said at most once during the 45 min)

- "**This is a bilateral matching problem with P(send) x P(accept) as the optimization target, not a single P(click) ranker.**" (Bilateral twist callback)
- "**The product is a calibrated bilateral probability, not just a ranking -- that is the property that lets growth and safety thresholds compose.**" (MMoE-calibration twist callback)
- "**User-level randomization leaks treatment effect across friend edges; cluster randomization at Louvain communities is the unbiased counterfactual.**" (Network-effect twist callback)
- "**NRT bilateral signal is a state feature at score time, not a batch precompute -- recent-action decays in seconds.**" (NRT twist callback)
- "**Abuse-posture is an upstream admission gate before retrieval, not a post-hoc rerank.**" (Abuse-posture twist callback)
- "**Treating bilateral matching as a single weighted-loss task is a category error -- it forces a compromise that under-fits both heads.**" (Architectural-correctness callback)

## Reuse range (one-line note, full mapping in cd://96)

This row's MMoE multi-head bilateral + 5-channel retrieval funnel + NRT signal lane + cluster-randomized A/B + leave-one-cluster-out variance + SUTVA-violation diagnostic + cluster-canary circuit-breaker rollout shape is the canonical **bilateral matching** carve-up. For RecSys / list-level / T&S-classification mappings see the cd://96 hub and the sibling sd-golden rows (`sd://meta-reels-golden`, `sd://meta-top3-comments-golden`, `sd://meta-weapon-ads-golden`).

---

## Design Doc 强调话术 (verbatim closing sentences for interview / Design Doc / Code Review settings)

**Say these 4 lines verbatim**:

1. **「采用 MMoE multi-head bilateral ranker，shared bottom + two gating heads + two task towers，serving score 取 P(send) × P(accept) 的乘积，per-relationship-type calibrated -- 不是 single weighted-loss。」**
2. **「5 retrieval channels 并行 -- mutual / 2-hop / two-tower-HNSW-M32 / cohort / inferred-real-life -- channel-of-origin 作为 one-hot feature 保留给 ranker；单一 end-to-end retrieval 会把 5 种信号混成一损失。」**
3. **「NRT bilateral signal 在 score time join，60s end-to-end SLA，覆盖双侧 last-N-seconds accept/reject/block；daily batch 会漏掉 ~90% 的 recent-action 信号。」**
4. **「Cluster-randomized A/B at Louvain communities，leave-one-cluster-out 方差恢复，SUTVA-violation diagnostic 作为实验合约的一部分；user-level randomization 因 friend-edge spillover 已有 ~40% 偏差案底。」**

Why these 4 sentences are the killer ending:

Sentence 1 is the architectural commitment (MMoE multi-head as inductive structure for bilateral matching, not a hack). Sentence 2 is the retrieval-decomposition commitment (5 parallel channels + channel-of-origin one-hot as signal-type preservation). Sentence 3 is the NRT-state commitment (recent-action as score-time state feature, not batch precompute). Sentence 4 is the experimentation-process commitment (cluster-randomized A/B as the unbiased counterfactual under network spillover) -- the E5 boundary signal: you know the relationship between ML metric, network-effect counterfactual, and platform-value alignment, and refuse to collapse them into a single user-level A/B.
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
    """Idempotent UPSERT keyed on slug='meta-friend-rec-golden'."""
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
    """Run AC checks + meta_mlsd_canonical.yaml schema gates on the upserted row."""
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
        "MMoE multi-head bilateral ranker",
        "5 retrieval channels",
        "NRT bilateral signal",
        "Cluster-randomized A/B",
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

    # ----- meta_mlsd_canonical.yaml schema checks -----
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

    # R-90S-friend-rec-section5: dataflow + architecture must keep the 3 anchors.
    keep_anchors = [
        "MMoE multi-head bilateral",
        "cluster-randomized A/B",
        "NRT bilateral signal",
    ]
    for anchor in keep_anchors:
        if anchor.lower() not in (dataflow or "").lower():
            errs.append(
                f"R-90S FAIL: dataflow missing anchor {anchor!r} "
                "(L4+ Strong Moment forcing function)"
            )
        if anchor.lower() not in (architecture or "").lower():
            errs.append(
                f"R-90S FAIL: architecture missing anchor {anchor!r} "
                "(L4+ Strong Moment forcing function)"
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

    # sd_golden field char ranges (per schema).
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

    # R-NARRATIVE-prose-form: measurable_proxy thresholds (per schema).
    #   - bold_density_per_section_min: 3 (>=3 **bold** spans per apply_3rule section)
    #   - bullet_run_max_consecutive:   4 (>4 unbroken bullet lines = violation)
    #   - table_row_max:                3 (markdown tables with >3 body rows = violation)
    bold_re = re.compile(r"\*\*[^*\n]+\*\*")
    for col in apply_3rule_cols:
        body = prose_cols.get(col) or ""
        bold_count = len(bold_re.findall(body))
        if bold_count < 3:
            errs.append(
                f"R-NARRATIVE FAIL: {col} bold_density={bold_count} < 3"
            )

    bullet_line_re = re.compile(r"^\s*[-*]\s+", re.MULTILINE)
    for col in apply_3rule_cols:
        body = prose_cols.get(col) or ""
        run = 0
        max_run = 0
        for line in body.splitlines():
            if bullet_line_re.match(line):
                run += 1
                max_run = max(max_run, run)
            elif line.strip() == "":
                # blank line resets the consecutive count
                run = 0
            else:
                run = 0
        if max_run > 4:
            errs.append(
                f"R-NARRATIVE FAIL: {col} bullet_run_max={max_run} > 4"
            )

    # Table row count: contiguous lines starting with '|'; first row is header,
    # second is the separator (|---|---|), rest are body rows.
    for col in apply_3rule_cols:
        body = prose_cols.get(col) or ""
        in_table = False
        rows_seen = 0
        for line in body.splitlines():
            if line.lstrip().startswith("|"):
                rows_seen += 1
                in_table = True
            else:
                if in_table:
                    body_rows = rows_seen - 2  # subtract header + separator
                    if body_rows > 3:
                        errs.append(
                            f"R-NARRATIVE FAIL: {col} table_body_rows={body_rows} > 3"
                        )
                in_table = False
                rows_seen = 0
        if in_table:
            body_rows = rows_seen - 2
            if body_rows > 3:
                errs.append(
                    f"R-NARRATIVE FAIL: {col} table_body_rows={body_rows} > 3"
                )

    print(f"[OK] row id={rid} slug={slug}")
    print(f"     title={title[:60]}...")
    print(f"     display_order={disp_order}, total prose bytes={total_bytes}")
    for k, v in prose_cols.items():
        print(f"     {k}: {len(v or '')} chars")
    return errs


def main() -> int:
    """CLI entrypoint: upsert + validate the meta-friend-rec-golden row."""
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
