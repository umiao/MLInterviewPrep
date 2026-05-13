"""Seed: T-P0-869 [Meta-MLSD] Weapon Ads Classifier Golden -> system_designs.

INSERTs (or idempotently updates) the canonical Meta MLSD Weapon Ads Classifier
golden example as ``system_designs(slug='meta-weapon-ads-golden')``,
drawer-reachable via ``sd://meta-weapon-ads-golden``. This is a **T&S
classification** golden (NOT RecSys), sibling of ``sd://meta-reels-golden`` and
``sd://meta-top3-comments-golden``. Cross-link via cd://96 §1/§3 drawers (added
by T-P0-871).

Per schemas/meta_mlsd_canonical.yaml (rule R-NARRATIVE-prose-form, added
2026-05-13): sd-golden docs are now English oral-recital narrative scripts,
NOT bullet-heavy markdown notes. Each section opens with a declarative
one-sentence claim, runs bold-anchored substantive prose, and closes with a
trade-off / handoff sentence. >=3 **bold** spans per section; <=4 consecutive
bullets; <=3-row tables; first-person 'I' voice.

4 unique twists (the question's senior signal vs generic classification):

  1. Bidirectional liability asymmetry -- false-positive (taking down a legal
     gun-store ad) and false-negative (allowing an illegal sale) are
     asymmetric in legal cost, and the asymmetry FLIPS by jurisdiction.
     Implication: per-region calibrated thresholds, not a single global.
  2. Multi-modal multi-layer adversarial -- text obfuscation, image OCR
     evasion, landing-page cloaking, seller identity rotation. Implication:
     OCR + CLIP + seller-graph trio, weekly adversarial-eval retrain.
  3. Platform admission posture upstream constraint -- ML model serves the
     policy regime (allow / limit / block), not the other way. Implication:
     cascade outputs calibrated to a SHARED scale so policy thresholds
     compose across stages.
  4. Legal-adjacent boundary as the true ML hard problem -- weapons-legal in
     Texas vs illegal in NY, sport-knife vs threat, verified vs unverified
     seller. The hard problem is NOT classification; it is jurisdiction-
     context-conditional adjudication. Implication: disagreement-aware
     label + counterfactual hard-neg shortcut audit.

Key content anchors (from task description T-P0-869):

  - cascade calibration shared scale (3-stage funnel: cheap pre-screen ->
    multimodal main classifier -> human escalation, all on the SAME P(weapon)
    scale so admission-policy thresholds compose).
  - OCR + CLIP + seller-graph trio (3 modalities feeding the main tower; OCR
    extracts text-in-image to defeat caption-only obfuscation; CLIP gives a
    distilled visual prior with adversarial training; seller-graph propagates
    identity / past-violation through a 2-hop GNN).
  - Three eval-set discipline (frozen golden + rolling weekly + adversarial
    red-team -- each answers a different question; do NOT collapse to one).
  - Disagreement-aware label (when reviewers split, use the variance as a
    feature in the uncertainty head, NOT a majority-vote single label).
  - Hard-neg shortcut counterfactual audit (each hard-neg item gets one
    attribute perturbed; if prediction flips on a non-causal attribute, the
    model is taking a shortcut).

Target row shape (9 prose columns, R-NARRATIVE-prose-form, char-range schema):

  - overview                : Phase 1 framing -- 2-paragraph anchor + 4 twists + 4-slot map
  - architecture            : 3-stage cascade + OCR+CLIP+seller-graph trio + calibration twist
  - dataflow                : Phase 2 verbatim walk (framing / metric+label / feature / model+serving)
  - formulas                : cascade calibration, disagreement-aware label, hard-neg shortcut audit
  - production_constraints  : weekly retrain cadence + three-eval-set + policy-threshold rollout
  - tradeoffs               : 8 numbered decisions ("I pick A because X, costs Y, switches to B if Z")
  - defense                 : Phase 3 -- 4 Strong Moment verbatim + tradeoff close
  - verbal_outline          : Weapon-Ads-specific entry phrases + drift recovery (methodology = cd://96)
  - cheat_sheet             : Weapon-Ads-only quantification anchors + firm-claim register + 4 Design-Doc 强调话术

Architecture and production_constraints both embed a short anchor sentence
pointing to fr-node ``meta-prep/system-design-must-knows/cascade-calibration``
(id=267) for the deep-version cascade-calibration walkthrough; the deep version
is owned by a separate fr-node task.

Idempotent: re-running upserts in place by `slug`. Sentinel-based UPSERT keyed
on `slug='meta-weapon-ads-golden'`.

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
    "Meta MLSD Golden Example -- canonical 4-twist T&S framing "
    "(bidirectional liability asymmetry / multi-layer adversarial / "
    "platform admission posture / legal-adjacent boundary) + 3-stage cascade "
    "classifier with shared-scale calibration. Adjacent to "
    "sd://meta-reels-golden and sd://meta-top3-comments-golden; "
    "cross-link via cd://96 §1 timing skeleton + §3 Strong Moments drawer."
)
DISPLAY_ORDER = 132
SOURCE_PATH = "docs/prep/meta_mlsd_2026-05-13_weapon_ads/source_06_weapon_ads_classifier_rewritten.md"

ANCHOR_FR_NODE = "meta-prep/system-design-must-knows/cascade-calibration"


OVERVIEW = """\
# Weapon Ads Classifier -- 45min Golden Walkthrough

**I'd reframe this as a T&S admission-cascade problem, not a binary classifier**, and that reframe is where the senior signal lives. The model serves the **policy regime** -- allow, limit, block -- producing calibrated P(weapon) for policy thresholds that vary by jurisdiction and seller posture. The unique angle: **four intrinsic twists** -- bidirectional liability asymmetry, multi-modal multi-layer adversarial, platform admission posture as upstream constraint, and the legal-adjacent boundary as the true ML hard problem -- drive almost every downstream decision. Methodology (timing skeleton, vocab YES/NO, 8 rhythm meta-rules, E4/E5 boundary) lives in `cd://96`; this row owns only the solution.

## Twist 1 -- Bidirectional liability asymmetry

A false positive that takes down a **federally-licensed gun-store ad** costs Meta in regulatory complaints from FFL holders; a false negative that lets through an **illegal private weapon sale** costs Meta in DOJ subpoena. **I pick** **per-region calibrated thresholds on a shared probability scale**, not a single global cutoff, because the FP-vs-FN cost ratio **flips by jurisdiction** -- in Texas the FP cost is higher, in New York the FN cost is higher. **Costs**: a region x category threshold table (~60 cells) on weekly recalibration. **Switches to** a global threshold only if regulatory cost equalizes -- not the regime we are in. This is where the cascade-calibration twist of Strong Moment #3 lives.

## Twist 2 -- Multi-modal, multi-layer adversarial

Adversaries evade single-modality detectors by **rotating the medium**: OCR-readable price moved into the image, banned terms transliterated, landing-page cloaked, seller identity rotated across new accounts. **I pick** an **OCR + CLIP + seller-graph trio** feeding the main tower: OCR text to defeat caption-only obfuscation, a CLIP visual prior fine-tuned with adversarial augmentation, and a **2-hop seller-graph GNN** propagating past-violation identity via shared payment instruments and addresses. **Costs**: three modality pipelines plus a seller-graph refreshed every 6 hours. **Switches to** OCR + caption-only if image-CLIP serving budget is cut, at the cost of a measurable adversarial-recall drop.

## Twist 3 -- Platform admission posture is upstream

The model output does not directly produce a take-down; it produces a **calibrated P(weapon)** that the **admission-policy layer** combines with seller-verification posture, jurisdiction, and product-category context. **I pick** a **cascade with shared-scale calibration** -- cheap pre-screen, multi-modal main classifier, human-review escalation -- so that policy thresholds **compose** across stages on the same posterior. **Costs**: temperature-scaling each stage on a shared validation set plus a weekly drift gate. **Switches to** an end-to-end joint model only if calibration becomes the bottleneck, which empirically it is not.

## Twist 4 -- Legal-adjacent boundary IS the ML hard problem

The hard problem is the **legal-adjacent middle** -- sport-knife in a hunting publication, antique-firearm collectible, verified FFL seller, jurisdictional carve-outs. **I pick** **disagreement-aware labeling** (reviewer variance becomes a feature in the uncertainty head and routes items to escalation) plus a **hard-neg shortcut counterfactual audit** (perturb one attribute; if prediction flips on a non-causal attribute, the model is shortcutting). **Costs**: an uncertainty head plus a weekly counterfactual job. **Switches to** majority-vote only if reviewer-pool size collapses below quorum.

## 4 Strong Moment slots (pre-allocated, do NOT improvise)

The 4 slots fire at fixed times. **Slot #1 (0-1)** carries the 4-twist framing with the "admission cascade, not binary classifier" reframe and the 15/25 time plan. **Slot #2 (8-12)** carries disagreement-aware labeling and LLM-teacher distillation, gated by three-eval-set discipline. **Slot #3 (15-21)** carries the OCR + CLIP + seller-graph trio with shared-scale temperature and the per-region threshold table. **Slot #4 (31-35)** carries the counterfactual shortcut audit, the frozen / rolling / adversarial eval tour, and the circuit-breaker rollout. The dataflow / defense / tradeoffs columns are the solution body; verbal_outline + cheat_sheet hold only Weapon-Ads-specific anchors -- anything else (rhythm rules, vocab YES/NO, E4/E5) belongs in `cd://96`.
"""


ARCHITECTURE = """\
# Architecture: 3-Stage Admission Cascade + OCR+CLIP+Seller-Graph Trio + Shared-Scale Calibration

## Decision summary (the architectural twist)

**I pick** a **3-stage admission cascade** -- cheap pre-screen, multi-modal main classifier, human-review escalation -- with **all three stages calibrated to a shared P(weapon) scale** so the admission-policy layer can compose thresholds across stages without re-deriving cutoffs. **This is where** the cascade-calibration twist of Strong Moment #3 lives. The **unique angle** versus a flat binary classifier is the OCR+CLIP+seller-graph trio feeding the main tower, plus an uncertainty head that surfaces disagreement directly rather than collapsing it. Latency: **cheap pre-screen p99 < 5 ms** on every ad creative, **main classifier p99 < 80 ms** on the ~2-5% that survive, **human escalation queue < 4 hours SLA** for items the model marks uncertain.

## Stage 1 -- cheap pre-screen (every ad creative)

A small **distilled student model** (a few-hundred-million-parameter image tower plus a tiny text tower) runs **synchronously on creative submission**. It removes the obvious **>=95% of clearly-not-weapon traffic** so the expensive main classifier sees only the **2-5% that warrants OCR + CLIP + seller-graph**. **I pick** a distilled student because the teacher is an LLM-multimodal model whose inference budget is two orders of magnitude too large for every ad; the student preserves **~98% of teacher recall at ~5%** of cost. **Costs**: a weekly distill-refresh job and a frozen-set tracker on student-vs-teacher gap. **Switches to** rule-based pre-screen only if compute is cut, but accepts an adversarial-recall drop.

## Stage 2 -- multi-modal main classifier (the core, expand ~90s)

The main tower fuses **three modalities**: OCR text from the image (defeats caption-only obfuscation), a **CLIP image encoder** fine-tuned with adversarial augmentation, and a **2-hop seller-graph GNN** propagating past-violation identity via shared payment-instrument and address edges. The tower carries two heads -- a **weapon-classification head** (BCE, calibrated) and an **uncertainty head** (variance over reviewer-disagreement labels). The uncertainty head is **not** Bayesian-dropout MC; it is a direct supervised target on disagreement variance -- the cheap operational way to get a routing signal.

Fusion is **late-fusion concat over modality embeddings**, not early fusion, because **OCR text drops in and out** as adversaries shift modalities, and late fusion degrades gracefully when one modality is missing. **Switches to** early fusion only if a single end-to-end transformer beats late-fusion concat by >=2 points on adversarial recall, which has not been the case at this scale.

## Stage 3 -- human-review escalation (the uncertain middle)

Items where the uncertainty head is **above a calibrated threshold** OR the main classifier sits in the **policy gray-zone** (P(weapon) between region-specific allow and block cutoffs) are queued for **human review with a 4-hour SLA**. Reviewer outputs feed back into the label store with **per-reviewer skill weights** plus the original disagreement variance. **This is the operational backbone** for the disagreement-aware label twist.

## Why a cascade, not a single big model

A single end-to-end model would force every ad creative through OCR + CLIP + seller-graph + LLM teacher. That is **two orders of magnitude over budget** at Meta's ads QPS. The cascade is **a serving-cost decomposition** (cheap stage handles 95%+ of traffic) **and a calibration decomposition** (each stage has clean precision-recall) simultaneously. **Switches to** end-to-end only if budget becomes unconstrained.

==> Section-stitch: the 3 modalities map back to Twist 2's adversarial-layers list, and the shared calibration scale delivers what Twist 3 promised on admission-policy composability.

## Cascade Calibration digest (this section self-contained -- deep version in fr-node)

**3-sentence core**:

1. **Shared-scale temperature**: each stage's logit is temperature-scaled on a shared validation set so that **P_stage1(weapon) = P_stage2(weapon) = P_main(weapon)** as a calibrated posterior, not just a ranking. Without this, the policy threshold at stage 1 means a different prior probability than the threshold at stage 2, and **cascade thresholds do not compose**.
2. **Per-region calibration**: temperature scaling is **per-jurisdiction** because the base rate of weapon ads varies by region; a single global temperature would over-pull the U.S.-Texas region and under-pull the New-York region. **Costs**: a region x category temperature table refreshed weekly.
3. **Drift gate**: calibration drift is checked nightly via **ECE (expected calibration error) on a frozen golden set**, and any single-region ECE > 2% triggers a manual review block on threshold rotations -- a circuit-breaker, not a manual review.

**Deep version in fr-node `""" + ANCHOR_FR_NODE + """`** -- covers temperature scaling vs Platt scaling vs isotonic regression for cascade outputs, the calibration-decomposition theorem under domain shift, and the operational checklist for region-specific recalibration. A separate fr-node task owns that 深版.

## Architectural choices -> 4 twists (callback)

The OCR + CLIP + seller-graph trio answers Twist 2 (multi-modal adversarial). The shared-scale temperature scaling answers Twist 3 (admission-posture). The uncertainty head + human-review escalation answers Twist 4 (legal-adjacent middle). And per-region thresholds answer Twist 1 (bidirectional liability asymmetry). **Each architectural decision callback to a framing twist** -- this is the property the cascade was designed for.
"""


DATAFLOW = """\
# Dataflow: 4-Section Verbatim Walkthrough (Phase 2 -- 15min framing + body)

## Decision summary (the rhythm twist)

**I pick** a chronological 4-section walk over a component-by-component walk because **the core decision here is** time-allocation: 4 Strong Moments at fixed slots (0-1 framing / 8-12 label / 15-21 architecture / 31-35 monitoring), and **this is where** E4 vs E5 wrap diverges. The walk follows the canonical body order **framing -> metric+label -> feature -> model+serving**, with scale anchors named verbatim: **p99 < 80 ms** on the main classifier, **>=95%** of traffic absorbed by the cheap pre-screen, **2-5%** reaching the main tower.

## Section 1: Framing (90s)  <- Strong Moment #1

"L1 (user): **The user of this ML output is the admission-policy layer**, not the end viewer. The viewer is downstream; the upstream constraint is Meta's content policy, which decides allow / limit / block based on the calibrated P(weapon) we produce.

L2 (scale): **Meta ads ingest a few million creative submissions per day across O(100) regulatory regions; per-region weapon-ad base rate ranges from 0.05% to 0.5%**, so the imbalance is real but not extreme. SLA: **synchronous block at submission for clearly-violating creatives** (cheap stage), **asynchronous block for the multi-modal-stage** (within minutes), **human review within 4 hours** for the uncertain middle.

L3 (twists with implications):

- **Bidirectional liability asymmetry** -> per-region calibrated thresholds, not global cutoff
- **Multi-modal multi-layer adversarial** -> OCR + CLIP + seller-graph trio, weekly adversarial-eval retrain
- **Platform admission posture upstream** -> cascade with shared-scale calibration so policy thresholds compose
- **Legal-adjacent middle IS the ML hard problem** -> disagreement-aware label + counterfactual hard-neg audit

L4 (ML formulation): **3-stage cascade classifier** -- cheap pre-screen, multi-modal main, human escalation -- with main tower outputting calibrated P(weapon) plus an uncertainty head. Retrieval is N/A because this is a classification problem, not a recommendation problem."

==> Section-stitch: each of these 4 twists hooks into a specific downstream metric, label rule, or serving constraint.

## Section 2: Metrics and Labels (180s)  <- Strong Moment #2

"**L1 North-star is policy-violation-recall on a frozen golden set, not raw classification accuracy**. Accuracy is dominated by the negative class; recall on policy-violations is the metric that aligns with regulatory exposure.

**L2 Proxies**, each with a one-line alignment statement:

- Precision at the **block threshold** -> false-positive cost on FFL-licensed sellers
- Recall at the **limit threshold** -> false-negative cost on unverified-seller weapon ads
- AUPRC on the **adversarial-red-team set** -> robustness against active evasion

**Three-eval-set discipline (the non-negotiable structure -- this section's senior signal)**:

- **Frozen golden set** answers 'does the model meet a fixed bar?' -- never updated, prevents drift in the metric itself.
- **Rolling weekly set** answers 'how is the model doing on this week's traffic?' -- refreshed every Monday from the prior week's reviewed sample.
- **Adversarial red-team set** answers 'how does the model do against active evasion?' -- continuously updated by an internal red team plus mined from production-flagged-but-classifier-missed items.

**Do NOT collapse these to one eval-set** -- each answers a different question, and a model that looks good on one can be silently broken on another.

**Disagreement-aware label (the core difficulty)**:

- **Explicit positive**: confident reviewer consensus (3+ reviewers agree).
- **Explicit negative**: confident reviewer consensus on not-weapon.
- **Disagreement region (the ML hard part)**: when reviewers split, the **variance is recorded as a label signal** for the uncertainty head; the **majority label is recorded as the classification target with a sample-weight reduction**; and the item is **promoted to the rolling eval set with an 'ambiguous-middle' tag**.

The disagreement-aware label is **strictly stronger** than majority-vote because majority-vote discards the variance entirely, and on legal-adjacent items the variance IS the signal the policy layer needs.

**LLM-teacher distillation** (label-scarcity solver): an LLM-multimodal teacher provides **soft labels** on bulk inference for the **non-reviewed long tail**; the student model is distilled with **KL divergence to the soft label** plus the human-reviewed hard labels weighted higher. This is the standard distill pattern for the bad-ads / relevance class of question, called out by name in the family taxonomy.

**Imbalance handling**: stratified sampling at training plus class-weighted loss; bandit exploration is N/A here because the cost of a single false negative is regulatory, not a UX experiment."

==> Section-stitch: the disagreement-aware label defines the two heads (classification + uncertainty) that the architecture in Section 4 will need.

## Section 3: Features (60s) -- 4-quadrant model

"**4-quadrant model, but the heaviest quadrant is item-side**:

**Ad creative (item-side, the dominant quadrant)**:

- **OCR-extracted text** from image (defeats caption-only obfuscation; this is where the multi-modal twist pays off)
- **CLIP image embedding** fine-tuned with adversarial augmentation -- random crops, color jitter, text overlays scrubbed from training pairs
- Caption + landing-page text (with cloaking-detection via crawler-as-end-user parity)

**Seller (the relational quadrant -- this is where the seller-graph twist lives)**:

- Past violation count + days-since-last-violation, decayed
- **2-hop seller-graph features**: shared payment instrument, shared physical address, shared device fingerprint -- aggregated via GNN with a 6-hour refresh
- Verification status: FFL-licensed, identity-verified, neither

**Context**:

- Region (jurisdiction-coded for the per-region threshold table)
- Ad placement surface + audience targeting overlap with weapon-interest categories
- Time of submission, recent appeals queue depth

**Interaction (creative x seller-history)**:

- Whether THIS seller has previously run THIS exact image (re-uploaded after takedown)
- Edit-distance between this caption and prior-violation captions from the same seller-graph cluster

**Critical distinction**: Seller-graph features are **per-(seller, time) pair**, recomputed every 6 hours on the seller-graph snapshot. This is the root of why a multimodal-only classifier is insufficient -- without identity propagation, a banned seller respawns and clears, and the classifier never sees the link."

==> Section-stitch: the 3 modalities (OCR + CLIP + seller-graph) feed the late-fusion concat in the main tower; the seller-graph features cross with the per-region threshold table at policy time.

## Section 4: Model and serving (60s)

"**Main tower is late-fusion concat over OCR + CLIP + seller-graph embeddings**, two heads: classification (BCE, temperature-scaled) and uncertainty (regression on disagreement variance). **I pick** late fusion over early fusion because **OCR text drops in and out** as adversaries shift modalities, and late fusion **degrades gracefully** when one modality is missing.

**Cascade composition**: stage-1 cheap pre-screen handles >=95% of traffic with a distilled student; stage-2 main tower handles 2-5% with the full trio; stage-3 human escalation handles the uncertain middle inside a **4-hour SLA**. **All three stages output calibrated P(weapon) on a shared scale**, which is the property that makes admission-policy thresholds compose.

**Latency budget**: cheap stage **p99 < 5 ms**, main stage **p99 < 80 ms**, human queue **< 4 hour SLA**. Throughput: a few million ad creatives per day, peaks at submission-spike events (election seasons, regulatory deadlines) at **~10x average**.

**Retrain cadence**: main classifier **weekly retrain**; seller-graph refresh **every 6 hours**; calibration **nightly drift check** on the frozen set; uncertainty head **weekly with the classifier**; LLM teacher distillation **monthly** (teacher is expensive)."

==> Section-stitch: the cascade composability + per-region thresholds set up the production_constraints section's three-eval-set discipline and the rollout circuit-breaker.
"""


FORMULAS = """\
# Cascade Calibration + Disagreement-Aware Label + Hard-Neg Shortcut Audit (3 anchors)

## Cascade calibration (shared-scale temperature)

Each stage `s` outputs a raw logit `z_s` from its modality-specific tower. Calibration applies a per-stage, per-region temperature `T_{s,r}` learned on a held-out validation set:

```
P_s(weapon | x, region=r) = sigmoid(z_s / T_{s,r})
```

The property we enforce: for any held-out item `x` reviewed by humans, `P_1(weapon | x, r) ~= P_2(weapon | x, r)` on the overlapping support, so the cascade thresholds **compose**. Equivalently, the expected calibration error (ECE) on the frozen golden set is bounded below 2% per region:

```
ECE_{s,r} = sum_b | accuracy(bucket_b) - mean_pred(bucket_b) | <= 0.02
```

If any single (stage, region) cell breaches 2%, **the threshold rotation pipeline halts** -- a circuit breaker, not a manual review.

## Disagreement-aware label

For an item reviewed by `n` reviewers with binary label vote `y_i in {0, 1}`, the label store records three quantities:

```
y_consensus   = round(mean(y_i))               # the classification target
w_consensus   = 1 - 2 * variance(y_i)          # sample-weight, low when reviewers split
variance(y_i) = mean(y_i) * (1 - mean(y_i))    # the uncertainty target
```

The classification head trains on `(y_consensus, w_consensus)` and the uncertainty head trains directly on `variance(y_i)`. This is strictly stronger than majority-vote because **the variance is preserved as a separate supervised signal**, not discarded.

## Hard-neg shortcut counterfactual audit

For each hard-negative item `x` (high P(weapon), human-labeled negative), generate counterfactual variants `x'` by perturbing one attribute at a time -- swap seller identity, replace caption, swap landing-page domain -- and measure the prediction shift:

```
shift_attr(x, attr) = | P(weapon | x) - P(weapon | x_perturbed(attr)) |
```

If `shift_attr(x, attr) > 0.3` for a **non-causal attribute** (seller identity when caption + image are unchanged, for instance), the model is taking a shortcut. The audit runs weekly on a sample of ~1000 hard-negs; **any shortcut rate above 5% triggers a feature-importance re-weight in the next retrain**.

## Three eval-set discipline (formal definition)

| Eval Set       | Refresh         | Answers                                      |
|----------------|-----------------|----------------------------------------------|
| Frozen golden  | Never           | Does the model meet a fixed regulatory bar?  |
| Rolling weekly | Mondays         | How is the model doing on this week's mix?   |
| Adversarial    | Continuous      | Robustness against active evasion?           |

**Each row answers a distinct question; do NOT collapse to a single eval-set** -- a model can look good on the frozen set and be silently broken on adversarial. The senior signal is naming all three and saying when to read which.
"""


PRODUCTION_CONSTRAINTS = """\
# Production Constraints: Weekly Retrain + Three-Eval-Set + Policy Threshold Rollout

## Decision summary (the production twist)

**I pick** a weekly main-classifier retrain, six-hour seller-graph refresh, nightly calibration drift check, and a three-eval-set discipline that runs continuously alongside a circuit-breaker rollout for policy thresholds -- **this is where** the cascade-calibration twist meets the wire. **Throughput**: a few million ad creatives per day, **submission-spike peaks ~10x average**, with **p99 < 80 ms** on the main stage and **<= 4 hours** SLA on human escalation. The unique angle versus a generic classifier deployment is the **policy threshold rollout is the actual change-management surface**, not the model weights.

## Latency budget and cascade composition

The cheap pre-screen runs **synchronously on creative submission with p99 < 5 ms**, absorbing >=95% of traffic. Items that survive flow into the main classifier asynchronously within a few seconds at **p99 < 80 ms** -- asynchronous because the OCR + CLIP + seller-graph trio plus the per-region temperature lookup is not on the submission-blocking path. Items the main classifier marks uncertain enter the human-review queue with a **4-hour SLA**, and items above the block threshold flow to the policy layer for immediate action. The serving-cost decomposition is the cascade -- without it, we would be running OCR + CLIP + seller-graph on every ad creative, which is **roughly two orders of magnitude over budget at Meta's ads QPS**.

## Retrain cadences (tiered, not one-size-fits-all)

| Cadence              | What                                                                        |
|----------------------|-----------------------------------------------------------------------------|
| Streaming 6h         | seller-graph GNN refresh, recent-violation propagation, identity rotation   |
| Nightly              | calibration drift check (ECE per region x stage), threshold rotation gate   |
| Weekly               | main classifier retrain, uncertainty head, distilled student refresh        |

**Key**: the seller-graph must refresh **every 6 hours**, otherwise a banned seller respawns under a new account and the classifier never sees the identity link. The weekly main retrain is fast enough for adversarial drift inside this class; **switches to** a 2-day cadence only if the adversarial-eval set degrades by **>=3 points week-over-week**.

## Three-eval-set discipline in production

The three eval-sets each gate a different decision: the **frozen golden set** gates a threshold rotation (does the new threshold preserve the regulatory bar?), the **rolling weekly set** gates a retrain release (does the retrained classifier hold up against this week's mix?), and the **adversarial red-team set** gates the seller-graph refresh policy (is identity propagation keeping up with evasion?). **No eval-set is a passive scoreboard** -- each one has a corresponding production action it gates.

## Policy threshold rollout (the actual change-management surface)

A new region-specific threshold rolls out via **shadow scoring + 1% canary -> 5% -> 25% -> 100%**, with **automatic halt** when any of three guardrails breaches: per-region ECE > 2%, false-positive rate on FFL-verified sellers > baseline + 10%, or false-negative rate on the adversarial red-team set > baseline + 5%. The unique structure here is that **policy thresholds rotate more often than model weights** -- regulatory environments change faster than the ML release cadence, so threshold-rotation is its own independent change-management lane.

## Cascade Calibration Production digest (self-contained -- deep version in fr-node)

The 2-piece skew defense in production is:

1. **Stage-skew audit**: every stage logs its calibrated P(weapon) for items that also reach the downstream stage; pair-correlations are monitored weekly. If `corr(P_1, P_2) < 0.85` on the overlapping support, calibration is broken between stages and the cascade does not compose -- the audit raises a P1 alert.
2. **Online-offline calibration parity**: the calibration temperatures are computed offline on the validation set; online, the same temperature is applied. A **periodic recomputation on online-served data** confirms the offline temperature still holds, and any divergence > 5% triggers a threshold-rotation freeze.

**Deep version in fr-node `""" + ANCHOR_FR_NODE + """`** -- covers temperature scaling vs Platt vs isotonic, the calibration-decomposition theorem under domain shift, and the per-region threshold-table refresh protocol. A separate fr-node task owns that 深版.

## Production scar (E4 senior signal -- one or two sentences total)

**In my past work**, we found that when the seller-graph refresh window was set to 24 hours, banned sellers were respawning under new accounts inside the window and clearing the classifier; the **fix was a 6-hour refresh plus a payment-instrument-based hash join** at submission. **One thing we learned the hard way** is that the cascade looked calibrated on the frozen set but was silently miscalibrated on the rolling weekly set after a base-rate shift in one region -- the **fix was per-region temperature plus the nightly ECE drift gate**, not a single global recalibration.
"""


TRADEOFFS = """\
# Tradeoffs (8 decision points -- each "I pick A because X, costs Y, switches to B if Z")

## Decision summary (the tradeoff twist)

8 tradeoffs follow, each in the form **"I pick A because X, costs Y, switches to B if Z"**. **This is where** the architectural twists meet concrete numbers: 2-5% main-tower traffic, p99 < 80 ms, 6-hour seller-graph refresh, weekly classifier retrain, 4-hour human-review SLA, per-region thresholds across O(100) jurisdictions, three eval-sets, and a 2% ECE drift gate.

1. **Cascade vs single end-to-end model** -- I pick a 3-stage cascade because it is **a serving-cost decomposition (cheap stage absorbs >=95% of traffic) and a calibration decomposition (each stage has clean precision-recall) simultaneously**. Costs: three calibration windows + a stage-skew weekly audit. Switches to end-to-end only if compute budget becomes unconstrained -- which is not the regime here.

2. **Shared-scale calibration vs per-stage independent thresholds** -- I pick shared-scale temperature so admission-policy thresholds **compose** across stages on the same posterior. Costs: a per-stage temperature table refreshed weekly plus a nightly ECE drift gate. Switches to per-stage independent thresholds only if calibration overhead becomes prohibitive, but that **costs the ability to reason about policy at the cascade level**.

3. **Per-region thresholds vs global threshold** -- I pick per-region calibrated thresholds because the bidirectional liability asymmetry **flips by jurisdiction** -- in Texas the FP cost is higher, in New York the FN cost is higher. Costs: a region x category table (~60 cells) refreshed weekly. Switches to a single global threshold only if regulatory cost equalizes across regions, which is not where regulation is heading.

4. **Disagreement-aware label vs majority-vote** -- I pick disagreement-aware labeling because the variance IS the signal the policy layer needs on legal-adjacent items, and the uncertainty head turns it into a calibrated routing signal. Costs: a second supervised head + per-reviewer skill weights in the label store. Switches to majority-vote only if reviewer-pool size collapses below quorum, which is a staffing problem **at the cost of** ML hard-problem fidelity.

5. **OCR + CLIP + seller-graph trio vs CLIP-only** -- I pick the trio because adversaries **rotate the medium** (text moves into the image, seller identity rotates), and any single modality has an adversarial-evasion budget that closes quickly. Costs: three modality pipelines plus a 6-hour seller-graph refresh. Switches to OCR + caption-only **if** the CLIP serving budget is cut, but accepts a measurable adversarial-recall drop.

6. **Late fusion concat vs early fusion transformer** -- I pick late fusion because OCR text drops in and out as adversaries shift modalities, and late fusion **degrades gracefully** when one modality is missing. Costs: a small loss on jointly-aligned modalities at scale. Switches to early fusion **if** a single end-to-end transformer beats late-fusion concat by >=2 points on the adversarial red-team set, which has not been the case at this scale.

7. **Three eval-sets vs one combined eval-set** -- I pick three eval-sets (frozen / rolling / adversarial) because each answers a different question (regulatory bar / this-week mix / active evasion robustness), and a single combined eval-set would silently mask one of the three. Costs: maintaining three eval pipelines + the discipline to read all three before a release. Switches to one combined eval **only if** label cost makes the discipline infeasible, but at the cost of release-time blindspots.

8. **LLM-teacher distillation vs scaled-up human labeling** -- I pick LLM teacher + student distill because human review is the bottleneck on labeling rare-class items at scale; the teacher provides soft labels on the long tail, and the student is **~98% of teacher recall at ~5% of cost**. Costs: a monthly teacher distill job + a frozen-set tracker on student-teacher gap. Switches to scaled-up human labeling **if** the teacher's calibration on legal-adjacent items collapses below ECE 5%, in which case humans become the only signal source.

Across all 8, the **firm-claim register** is: per-region thresholds, shared-scale calibration, OCR+CLIP+seller-graph trio, late-fusion concat, three-eval-set discipline, disagreement-aware labels, weekly classifier retrain with 6-hour seller-graph refresh, and LLM-teacher distillation with student deployment.
"""


DEFENSE = """\
# Strong Moments -- 4 verbatim English lines (say them as-is)

The 4 lines below are canonical Strong Moment shape, **internalized verbatim**. Drop them at 0-1 / 8-12 / 15-21 / 31-35 minute slots. Strong-Moment methodology lives in `cd://96` §3 / §5 / §6; this column carries only the speak-aloud English plus the close-out trade-off.

## Decision summary (which Strong Moment to fire when)

**I pick** the 4 Strong Moment slots at the 4 places where Weapon Ads diverges most: framing (4 twists + cascade reframe), label (disagreement-aware + LLM teacher), architecture (trio + shared-scale calibration), monitoring (counterfactual audit + three eval-sets). Each block follows Cue + verbatim + close-out trade-off. The **unique angle** is each Strong Moment **ends with a trade-off**, **this is where** E5 separates from a brain dump. Scale: **p99 < 80 ms** on the main stage, **submission peak ~10x**, **6-hour seller-graph refresh**, **weekly classifier retrain**.

---

## Strong Moment #1 -- Admission-Cascade Reframe + 4 Twists (0-1 min, opening)

**Cue**: declarative open "**I'd reframe this as a T&S admission-cascade problem, not a binary classifier** ... four twists."

> "**I'd reframe this as a T&S admission-cascade problem, not a binary classifier**. The model serves the policy regime -- allow, limit, block -- and produces calibrated P(weapon) feeding policy thresholds that vary by jurisdiction and seller posture.
>
> **Four unique twists vs generic classification, each with a design implication**.
>
> **First, bidirectional liability asymmetry** -- a false positive on a federally-licensed gun-store ad costs FFL regulatory complaints; a false negative on an illegal private sale costs DOJ subpoena. **The asymmetry flips by jurisdiction**. Implication: per-region calibrated thresholds on a shared probability scale.
>
> **Second, multi-modal multi-layer adversarial** -- adversaries rotate the medium, banned text moves into the image, landing pages cloak, seller identity rotates. Implication: an OCR + CLIP + seller-graph trio plus weekly adversarial-eval retrain.
>
> **Third, platform admission posture is upstream** -- the admission-policy layer combines our P(weapon) with seller verification, jurisdiction, product category. Implication: cascade with shared-scale calibration so policy thresholds compose.
>
> **Fourth, the legal-adjacent middle IS the ML hard problem** -- not the obvious rifle, but sport-knife in a hunting publication, antique collectible, verified-FFL compliant landing page. Implication: disagreement-aware labeling plus counterfactual hard-neg shortcut audit.
>
> Time plan: **15 / 25 min split**."

---

## Strong Moment #2 -- Disagreement-Aware Label + LLM Teacher (8-12 min)

**Cue**: "**Let me walk through the disagreement-aware label and the LLM-teacher distill**".

> "**The label is the core difficulty here, because the legal-adjacent middle is where reviewers themselves disagree, and the variance is the signal the policy layer needs**.
>
> **Confident reviewer consensus** -- 3+ reviewers agreeing -- gives an explicit positive or negative.
>
> **The disagreement region** is the ML hard part. I record three quantities per item: the **consensus label as the classification target**, a **sample-weight reduction proportional to disagreement variance**, and the **variance itself as a supervised signal for an uncertainty head** -- the operational route into the human-escalation queue.
>
> **Strictly stronger than majority-vote**, because majority-vote discards variance entirely, and on legal-adjacent items **the variance IS the signal**.
>
> **Long-tail label-scarcity** is solved with an LLM-multimodal teacher distilling into the student via KL divergence to soft labels plus human hard labels weighted higher. **The student preserves ~98% of teacher recall at ~5% cost** -- what makes a few-million-creative-per-day cascade economically feasible.
>
> **Three eval-sets gate three decisions**: frozen golden gates threshold rotations, rolling weekly gates retrain releases, adversarial gates seller-graph refresh policy. **Each has a corresponding production action**.
>
> Trade-off: disagreement-aware labeling **costs a second head plus per-reviewer skill weights**, in exchange for getting the legal-adjacent middle right."

---

## Strong Moment #3 -- OCR+CLIP+Seller-Graph Trio + Cascade Calibration (15-21 min)

**Cue**: "**Let me unpack two architectural decisions -- the trio main tower, and the shared-scale calibration**".

> "**The first architectural decision is the OCR + CLIP + seller-graph trio**. OCR extracts text-in-image to defeat caption-only obfuscation. CLIP gives a distilled visual prior fine-tuned with adversarial augmentation. The 2-hop seller-graph GNN propagates past-violation identity via shared payment instruments and addresses, refreshed every 6 hours so banned sellers cannot respawn faster than the graph sees them.
>
> **Fusion is late-fusion concat, not early fusion**, because OCR text drops in and out as adversaries shift modalities, and late fusion **degrades gracefully when one modality is missing**. Switches to early fusion only if an end-to-end transformer beats late-fusion concat by >=2 points on the adversarial set, which has not been the case at this scale.
>
> **The second architectural decision is the shared-scale calibration**. Each stage's logit is temperature-scaled per region on a held-out validation set, so **P_stage1, P_stage2, and P_main are calibrated to the same posterior**, not just the same ranking. Without this, **cascade thresholds do not compose**. Calibration is per-region because base rate varies by jurisdiction; a global temperature over-pulls Texas and under-pulls New York. Drift is checked nightly via ECE on the frozen golden set, with a 2% per-region cap as a circuit breaker -- not a manual review."

**Bonus closer (objective combination)**:

> "Two heads: classification trained with BCE on the consensus label + sample-weight reduction, plus an uncertainty head regressed on disagreement variance. **The classification head feeds the policy layer; the uncertainty head feeds the routing layer**. Combination is at the policy boundary, not inside a single weighted loss. **Treating uncertainty as a single composite score is a category error**."

---

## Strong Moment #4 -- Counterfactual Audit + Three Eval-Sets + Circuit-Breaker Rollout (31-35 min)

**Cue**: "**Let me zoom out and talk monitoring, eval discipline, and policy-threshold rollout**". This is the E5 boundary signal.

> "**Model health monitoring needs three things, ordered by signal latency**.
>
> **First, hard-neg shortcut counterfactual audit, weekly**. For each hard-neg, I perturb one attribute -- swap seller identity, replace caption, swap landing-page domain -- and measure the prediction shift. **If prediction flips on a non-causal attribute** like seller name, the model is shortcutting. Shortcut rate above 5% triggers a feature-importance re-weight in the next retrain. **This is earlier than precision-recall degradation** because it catches the model when it has learned the right answer for the wrong reason.
>
> **Second, three-eval-set discipline**, continuously. Frozen golden nightly as a regulatory-bar tracker; rolling weekly Mondays after refresh; adversarial red-team continuously with new evasion patterns mined from classifier-missed items. **Do not collapse these to one number**.
>
> **Third, online prediction-distribution drift**, hourly. KL divergence day-over-day catches base-rate shifts before the eval-sets do -- the leading-est indicator. Most candidates only say 'monitor AUC'; this is the senior signal.
>
> **Policy-threshold rollout is the actual change-management surface**, more than the model weights. A region-specific threshold rolls out via shadow + 1% / 5% / 25% / 100% canary, with **automatic halt** on three guardrails: per-region ECE > 2%, FFL-seller FP-rate > baseline + 10%, or adversarial FN-rate > baseline + 5%. **Circuit breaker, not manual review**.
>
> Loop closure: monitoring feeds **the training label store** (shortcut flags trigger re-weighting and hard-neg mining) and **the seller-graph refresh schedule** (drift escalates 6-hour to 1-hour during incidents).
>
> Trade-off: **policy thresholds rotate more often than model weights** -- regulatory environments change faster than the ML release cadence, so threshold-rotation is its own change-management lane. Want me to deepen any part?"
"""


VERBAL_OUTLINE = """\
# Weapon-Ads-specific verbal anchors (methodology lives in cd://96)

The general verbal scaffolding (declarative openers, sub-structure announce, drift recovery, ML-native YES/NO vocab table, hand-off / collaborative-mode phrasing, quantification phrasing, production-scar phrasing) lives in `cd://96` §5 (Framing / Body / Strong / Zoom 元结构) and §6 (8 偏好节奏 meta-rules). The lines below are the only ones unique to **Weapon Ads Classifier** -- quote them verbatim, do NOT duplicate cd96.

## 4 Strong Moment entry phrases (memorize verbatim -- these are the cue lines)

1. "**I'd reframe this as a T&S admission-cascade problem, not a binary classifier** ... four unique twists vs generic classification, each with a design implication." (4-twist framing, 0-1 min -- Twist 1/2/3/4)

2. "**The label is the core difficulty here, because the legal-adjacent middle is where reviewers themselves disagree, and the variance is the signal the policy layer needs**." (label, 8-12 min -- disagreement-aware twist)

3. "**The first architectural decision is the OCR + CLIP + seller-graph trio** ... **the second architectural decision is the shared-scale calibration**." (architecture, 15-21 min -- multi-modal + cascade-calibration twist)

4. "**Model health monitoring needs three things, ordered by signal latency** ... hard-neg shortcut counterfactual audit, three-eval-set discipline, online prediction-distribution drift." (monitoring + rollout, 31-35 min -- E5 wrap-up twist)

## Weapon-Ads-specific drift-recovery lines (NOT in cd96 -- these name Weapon Ads by surface)

When the interviewer drifts toward generic classification: "**Let me return to the ML core** -- for Weapon Ads the question is not the binary classifier, it is the admission-cascade composability under shared-scale calibration, because that is where regulatory exposure actually lives."

When asked about retrieval: "**Retrieval is N/A here** -- this is a classification problem on every ad creative, not a recommendation problem. The closest analog is the cheap pre-screen stage, which is a filter, not retrieval."

When asked about cold-start too early: "**Let me park new-seller cold-start until the seller-graph section** -- the 2-hop GNN with verified-identity priors handles it, and cold-start is most of the 'why a graph and not just features' answer."

When asked about scale at framing: "**A few million creative submissions per day across O(100) regulatory regions**, with submission-spike peaks at about 10x average. The cheap stage absorbs >=95% of traffic at p99 < 5 ms; the main stage handles 2-5% at p99 < 80 ms. The ML decisions here do not change with QPS, only the cheap-stage student capacity and seller-graph refresh window do."

## Weapon-Ads-only hand-off prompt (the deepen-which-side question)

> "Want me to **deepen the disagreement-aware label and LLM teacher distill, the OCR+CLIP+seller-graph trio with shared-scale calibration, or the three-eval-set discipline with the counterfactual hard-neg audit**?"

The 3-way choice maps to Weapon-Ads-specific levers: labels = disagreement-aware variance head + LLM teacher distillation + per-reviewer skill weights; architecture = OCR + CLIP + 2-hop seller-graph GNN + shared-scale temperature; monitoring = frozen / rolling / adversarial eval-sets + weekly counterfactual shortcut audit + circuit-breaker policy-threshold rollout. Avoid offering a 4th choice -- three is the canonical Weapon Ads carve-up.
"""


CHEAT_SHEET = """\
# 30-sec pre-walk-in checklist -- Weapon-Ads-only

Methodology (timing skeleton, 元结构, 8 meta-rules, E4/E5 boundary, drift-recovery vocab) lives in `cd://96` §1 / §5 / §6 / §8. The anchors below are Weapon-Ads-specific only -- quote verbatim, do NOT overlap cd96.

## Strong Moment slot map (memorize position, anchor, twist)

| Time   | Slot    | Weapon-Ads-specific anchor (the twist this slot hosts)                            |
|--------|---------|-----------------------------------------------------------------------------------|
| 0-1    | **#1**  | Admission-cascade reframe + 4 twists -- liability asymmetry / adversarial / posture / legal-adjacent |
| 8-12   | **#2**  | Disagreement-aware label + LLM teacher distill, 3 eval-sets gate 3 actions        |
| 15-21  | **#3**  | OCR+CLIP+seller-graph trio + shared-scale calibration per region                  |
| 31-35  | **#4**  | Counterfactual hard-neg shortcut audit + 3-eval-set discipline + circuit-breaker rollout |

## Weapon-Ads-only quantification anchors (drop verbatim into the appropriate moment)

- **15 / 25 min split**: 前段 framing / metric+label / feature / model+serving, 后段 production constraints + monitoring -- the Weapon Ads time plan declared in the first 60s.
- **>=95% cheap-stage absorbed, 2-5% main-stage**: the cascade-as-serving-cost-decomposition anchor.
- **p99 < 5 ms cheap stage, p99 < 80 ms main stage, <= 4 hour human-escalation SLA**: the 3-tier latency anchor.
- **6-hour seller-graph refresh, weekly main retrain, nightly calibration drift gate, monthly LLM teacher distill**: the tiered retrain cadence.
- **ECE <= 2% per region as the calibration drift gate**: the circuit-breaker threshold for policy rollouts.
- **Counterfactual audit weekly, shortcut rate threshold 5%**: the senior signal earlier than precision-recall.
- **3-stage rollout 1% / 5% / 25% / 100% with 3 guardrails (ECE / FFL-FP / adversarial-FN)**: the policy-threshold change-management lane.
- **Student preserves ~98% of teacher recall at ~5% of cost**: the LLM-teacher distill economics.

## Weapon-Ads-only firm-claim register (each line is said at most once during the 45 min)

- "**This is a T&S admission-cascade problem, not a binary classifier.**" (Twist framing callback)
- "**The asymmetry flips by jurisdiction -- in Texas FP cost is higher, in New York FN cost is higher.**" (Liability-asymmetry twist callback)
- "**Late fusion degrades gracefully when one modality drops in or out; that is the property a trio main tower needs.**" (Multi-modal twist callback)
- "**Cascade thresholds compose only if every stage is calibrated to the same posterior.**" (Cascade-calibration twist callback)
- "**Disagreement-aware labeling is strictly stronger than majority-vote, because on legal-adjacent items the variance IS the signal.**" (Legal-adjacent twist callback)
- "**Policy thresholds rotate more often than model weights -- threshold-rotation is its own change-management lane.**" (Production-twist callback)

## Reuse range (one-line note, full mapping in cd://96)

This row's 3-stage cascade + shared-scale calibration + OCR+CLIP+seller-graph trio + disagreement-aware label + 3-eval-set discipline + counterfactual shortcut audit + circuit-breaker policy rollout shape is the canonical **T&S classification** carve-up. For RecSys / list-level / bilateral-matching mappings see the cd://96 hub and the sibling sd-golden rows (`sd://meta-reels-golden`, `sd://meta-top3-comments-golden`, `sd://meta-friend-rec-golden` planned).

---

## Design Doc 强调话术 (verbatim closing sentences for interview / Design Doc / Code Review settings)

**Say these 4 lines verbatim**:

1. **「采用 3-stage admission cascade，每个 stage 的输出 calibrated 到 shared P(weapon) posterior，policy thresholds 在 cascade 上可组合。」**
2. **「OCR + CLIP + seller-graph 三 modality 用 late-fusion concat，单模态缺失时模型 degrade gracefully，对抗性 evasion 不会通过单一通道击穿。」**
3. **「Disagreement-aware label：reviewer variance 进入 uncertainty head，不被 majority-vote 抹掉；在 legal-adjacent middle 上严格强于 majority-vote。」**
4. **「Three eval-sets (frozen / rolling / adversarial) 各 gate 一个 production action；Policy threshold rotation 是独立的 change-management lane，不和 model weights 共用 release cadence。」**

Why these 4 sentences are the killer ending:

Sentence 1 is the architectural commitment (cascade-as-decomposition + shared-scale calibration as inductive structure). Sentence 2 is the multi-modal robustness commitment (late fusion + adversarial training as inference-correctness, not as a hack). Sentence 3 is the label-layer commitment (disagreement preserved as supervised signal, not noise). Sentence 4 is the production-process commitment (eval discipline and policy rollout as independent change-management lanes) -- the E5 boundary signal: you know the relationship between ML metric, regulatory exposure, and policy posture, and refuse to collapse them into a single number.
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
    """Idempotent UPSERT keyed on slug='meta-weapon-ads-golden'."""
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
        "采用 3-stage admission cascade",
        "OCR + CLIP + seller-graph 三 modality",
        "Disagreement-aware label",
        "Three eval-sets",
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
    """CLI entrypoint: upsert + validate the meta-weapon-ads-golden row."""
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
