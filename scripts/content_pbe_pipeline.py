"""Populate the pbe-pipeline system design module with all 8 content sections.

Usage:
    python scripts/content_pbe_pipeline.py

Finds the SystemDesign record with slug="pbe-pipeline" and fills in:
  overview, architecture, dataflow, formulas,
  production_constraints, tradeoffs, defense, verbal_outline

Idempotent -- overwrites existing content on each run.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

# ---------------------------------------------------------------------------
# S1: Overview & Motivation
# ---------------------------------------------------------------------------

OVERVIEW = r"""## Overview & Motivation

ML ranking models are only as good as their training data. At eBay, the search
ranking pipeline (Cassini) serves billions of impressions daily, but the training
signal historically relied on **clicks** -- a fundamentally flawed label source.

### Why Clicks Are Not Enough

- **Sparsity**: Click-through rate is only 2--5%. For 95%+ of impressions, we
  have *no signal at all* from click logs.
- **Position bias**: Users examine top positions disproportionately. An item at
  position 1 gets clicked not because it is the best, but because it is seen
  first.
- **Trust bias**: Users trust the ranking and click the top result even when
  lower results are more relevant.
- **Click != satisfaction**: A click followed by an immediate back-button is a
  *negative* signal, yet raw click logs count it the same as a 5-minute dwell.

### The PBE Approach

**Product-Based Experience (PBE)** logging replaces click-centric labels with
richer behavioral signals:

| Signal | What It Captures | Why It Matters |
|--------|-----------------|----------------|
| **Viewport exposure** | Whether the item was actually visible on screen | Eliminates position bias for unseen items |
| **Dwell time** | How long the user engaged with the item | Distinguishes genuine interest from accidental clicks |
| **Engagement depth** | Scroll depth, image zoom, add-to-cart | Multi-level relevance beyond binary click/no-click |

### Challenge

The pipeline must be **low-latency** (not degrade search response time),
**high-throughput** (~500M impressions/day), and **attributable** (every training
label traces back to the exact ranking model that produced it, enabling
counterfactual evaluation).
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------

ARCHITECTURE = r"""## Architecture Deep Dive

The PBE pipeline spans three layers: online serving, dual-stream ingestion, and
offline processing. Each layer is designed for a different latency/throughput
trade-off.

### Online Search Serving

```
[User Query]
    |
    v
[Search Front End] -- injects trackable IDs into HTML (data-track-id)
    |
    v
[Cassini Ranking Engine] -- produces ranked results with model attribution metadata
    |
    v
[PBE Carousel] -- enhanced product cards with viewport tracking (IntersectionObserver)
    |
    v
[Browser] -- fires viewport/dwell/engagement events to Sojourner
```

- **Search Front End**: Every rendered item receives a unique `data-track-id`
  attribute that encodes `(query_id, item_id, position, model_version)`.
  This is the foundation of attribution -- without it, we cannot trace a
  training label back to the model that ranked the item.
- **Cassini Ranking Engine**: Appends model attribution metadata to each result
  (which model scored it, which features were used, the raw score).
- **PBE Carousel**: Enhanced product experience that instruments viewport
  tracking via the `IntersectionObserver` API. Fires events when items enter
  and leave the viewport.

### Dual-Stream Data Ingestion

Two parallel streams feed the offline processing layer:

**Stream 1 -- Behavioral Events (Sojourner/UBI)**:
- Raw user events (impressions, viewport enter/leave, clicks, dwell, add-to-cart)
- Sojourner performs session stitching and ID resolution
- Spark Join at 5-minute micro-batches resolves anonymous events to user sessions

**Stream 2 -- Product Features (Kafka Feature Broker)**:
- Product metadata: price, condition, seller score, image quality, shipping speed
- Kafka Streams for low-latency feature updates
- Spark Streaming materializes feature tables partitioned by date

### Offline Processing & Attribution

- **Analytics Engine**: Computes per-impression labels: exposure boolean, dwell
  duration, engagement depth, conversion flag.
- **Formal Attribution**: Applies position bias correction (IPW) and multi-touch
  module attribution discount. This is the core intellectual contribution of
  the pipeline.
- **Training Data Materialization**: Joins attributed labels with features into
  typed ML/GPU-friendly format (Parquet), partitioned by `date + model_version`.

### ML Closed Loop

```
Training Data -> Model Training (LambdaMART / neural ranker)
    -> A/B Testing -> Deploy Ranking Policy -> New PBE Logs (closed loop)
```

Every model trains on data produced by its predecessor, creating a feedback loop
that the attribution layer must carefully manage to avoid feedback amplification.
"""

# ---------------------------------------------------------------------------
# S3: Data Flow
# ---------------------------------------------------------------------------

DATAFLOW = r"""## Data Flow & Key Components

### End-to-End Flow

```
User sees SRP (Search Results Page)
  |
  |-- Trackable IDs embedded in HTML via data-track-id attributes
  |
  +-- Stream 1: Behavioral Events
  |     User actions -> Sojourner (session stitch + ID resolution)
  |       -> Spark Join (5-min micro-batch, resolves anonymous -> session)
  |       -> Behavioral event tables (partitioned by date)
  |
  +-- Stream 2: Product Features
  |     Product updates -> Kafka Feature Broker
  |       -> Spark Streaming -> Feature tables (partitioned by date)
  |
  +-- Offline Attribution Pipeline (daily batch)
        |
        +-- Analytics Engine
        |     Joins Stream 1 + Stream 2
        |     Computes: exposure labels, dwell, engagement, conversion
        |
        +-- Formal Attribution
        |     Position bias correction (IPW weights)
        |     Module attribution discount (multi-touch credit)
        |
        +-- Training Data Materialization
              Parquet files: features + attributed labels
              Partitioned by date + model_version
              ~2TB per daily snapshot, 30-day retention
                |
                v
        ML Training -> A/B Test -> Deploy -> New Logs (closed loop)
```

### Key Component Details

#### Sojourner (Session Stitcher)

Sojourner is eBay's real-time event processing system that:
1. Receives raw UBI (Unified Behavioral Interface) events
2. Resolves anonymous browsing sessions to user IDs (when available)
3. Stitches page-level events into coherent sessions
4. Outputs enriched session events at ~200K events/sec peak

#### Spark Join (Micro-Batch Resolution)

The 5-minute micro-batch Spark job:
1. Reads Sojourner output from the last 5-minute window
2. Joins behavioral events with trackable ID metadata
3. Resolves `(data-track-id) -> (query_id, item_id, position, model_version)`
4. Writes resolved events to the behavioral event store

#### Analytics Engine (Label Computation)

For each impression in the resolved event stream:

| Label | Computation | Type |
|-------|------------|------|
| `exposed` | viewport duration > threshold AND visible percentage > 50% | Boolean |
| `dwell_seconds` | time between viewport-enter and viewport-leave/page-exit | Float |
| `engaged` | dwell > 2s OR image zoom OR add-to-cart | Boolean |
| `converted` | purchase within 24h of impression | Boolean |
| `satisfaction` | weighted combination of dwell, engagement, conversion | Float [0,1] |

#### Attribution Engine

Applies two corrections to raw labels:

1. **Position bias correction** via IPW (Inverse Propensity Weighting)
2. **Module attribution discount** for items appearing in multiple modules
"""

# ---------------------------------------------------------------------------
# S4: Formulas & Algorithms
# ---------------------------------------------------------------------------

FORMULAS = r"""## Formulas & Algorithms

### Viewport Exposure Detection

An item $i$ is considered **exposed** if it was visible in the user's viewport
for sufficient duration and area:

$$
\text{exposed}(i) = \mathbb{1}\bigl[\text{viewport\_dur}(i) > \tau \;\land\; \text{visible\_pct}(i) > 0.5\bigr]
$$

where $\tau$ is typically 1 second (configurable per experiment). The
`IntersectionObserver` API reports `visible_pct` as the ratio of the item's
bounding box that intersects the viewport.

### Position Bias Correction (IPW)

Users examine top positions more frequently, creating **position bias** in
behavioral labels. We correct this using Inverse Propensity Weighting:

$$
w_k = \frac{1}{P(\text{examine} \mid \text{pos} = k)}
$$

where $P(\text{examine} \mid \text{pos} = k)$ is estimated from **randomization
experiments**: for a small fraction (~0.1%) of queries, we randomly shuffle
results and measure examination rates by position.

The debiased label for item $i$ at position $k$ becomes:

$$
\text{label}_{\text{debiased}}(i) = w_k \cdot \text{label}_{\text{raw}}(i)
$$

Items at low positions that were still clicked/engaged get **upweighted**
(the model learns they are genuinely relevant, not just position-favored).

### Module Attribution Discount

On a modern SRP, the same item can appear in multiple modules (organic results,
sponsored carousel, "similar items" widget). Raw labels would **double-count**
the item's relevance. The multi-touch attribution discount distributes credit
proportionally to exposure:

$$
\text{label}_{\text{adj}}(i, m) = \text{label}_{\text{raw}}(i) \cdot \frac{\text{exposure}(i, m)}{\sum_{m'} \text{exposure}(i, m')}
$$

where $m$ indexes modules and $\text{exposure}(i, m)$ is the viewport duration
of item $i$ in module $m$.

### Position-Debiased LambdaMART

The ranking model (LambdaMART) is trained with IPW-weighted pairwise loss. For
a pair of documents $(i, j)$ where $i$ is preferred:

$$
\mathcal{L}_{\text{IPW}} = \sum_{(i,j)} w_{k_i} \cdot w_{k_j} \cdot \bigl|\Delta \text{NDCG}(i,j)\bigr| \cdot \log\bigl(1 + e^{-(s_i - s_j)}\bigr)
$$

where $s_i, s_j$ are model scores, $k_i, k_j$ are the positions, and
$\Delta\text{NDCG}(i,j)$ is the NDCG change from swapping $i$ and $j$ in the
current ranking.

### Satisfaction Score (Composite Label)

The final training label combines multiple signals into a single satisfaction
score:

$$
\text{satisfaction}(i) = \alpha \cdot \text{dwell\_norm}(i) + \beta \cdot \text{engaged}(i) + \gamma \cdot \text{converted}(i)
$$

where $\alpha + \beta + \gamma = 1$ and the weights are tuned via offline
evaluation (typically $\alpha = 0.3$, $\beta = 0.3$, $\gamma = 0.4$).
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints
# ---------------------------------------------------------------------------

PRODUCTION_CONSTRAINTS = r"""## Production Constraints

### Scale Numbers

| Metric | Value | Context |
|--------|-------|---------|
| **Impression volume** | ~500M impressions/day, ~2B viewport events/day | Each SRP renders 48--100 trackable items |
| **Click volume** | ~20M clicks/day (~2--5% CTR) | Sparse signal -- why viewport data is essential |
| **Stream 1 throughput** | ~200K events/sec peak (Sojourner) | Spark Join for ID resolution runs at 5-min micro-batches |
| **Stream 2 throughput** | ~50K feature updates/sec (Kafka) | Product features: price, condition, seller score, image quality |
| **Spark Join latency** | ~5 min end-to-end (event to resolved session) | Acceptable for offline training; not real-time |
| **Attribution processing** | Daily batch, ~4 hours on 500-node Spark cluster | Processes previous day's full session data |
| **Training data size** | ~2TB per daily snapshot (features + labels) | 30-day retention with date partitioning |
| **Model retrain cycle** | Daily for main ranker; weekly for experimental models | Full retrain on 14-day window of attributed data |
| **IPW estimation** | Updated monthly via position randomization experiments | ~0.1% of queries participate in randomization |

### Latency Budget

The PBE logging instrumentation must not degrade search latency:

| Component | Latency Budget | Approach |
|-----------|---------------|----------|
| Trackable ID injection | <1ms | Server-side, added during HTML rendering |
| IntersectionObserver setup | <5ms per page | Async, non-blocking, runs after page paint |
| Event beacon firing | 0ms (async) | `navigator.sendBeacon()` -- fire-and-forget |
| Sojourner ingestion | N/A (async) | Decoupled from search serving path |

### Storage & Retention

| Data | Format | Retention | Storage |
|------|--------|-----------|---------|
| Raw UBI events | Avro on HDFS | 90 days | ~50TB/day |
| Resolved behavioral events | Parquet on HDFS | 60 days | ~10TB/day |
| Feature tables | Parquet on HDFS | 30 days | ~5TB/day |
| Attributed training data | Parquet on HDFS | 30 days | ~2TB/day |
| IPW weight tables | CSV (small) | Indefinite | ~10MB/month |
"""

# ---------------------------------------------------------------------------
# S6: Trade-off Analysis
# ---------------------------------------------------------------------------

TRADEOFFS = r"""## Trade-off Analysis

| Decision | Option A | Option B | Our Choice & Why |
|----------|----------|----------|------------------|
| **Exposure tracking** | Click-only labels | Viewport-based (PBE) labels | **Viewport** -- clicks represent only 2--5% CTR. Viewport captures the 95%+ of items users saw but did not click, providing dense supervision. |
| **Feature logging** | Synchronous (inline with search response) | Asynchronous (Kafka) | **Async** -- synchronous logging adds 20--50ms to search latency, which violates our <5ms instrumentation budget. Kafka decouples feature capture from serving. |
| **Attribution model** | Last-touch (credit to last module seen) | Multi-touch with exposure weighting | **Multi-touch** -- items appear in multiple SRP modules (organic, carousel, ads). Last-touch over-credits the final module and under-credits discovery modules. |
| **Position bias handling** | None (trust raw labels) | IPW from randomization experiments | **IPW** -- without correction, models learn to replicate position bias rather than true relevance. The 0.1% randomization cost is negligible compared to the +1.8% NDCG gain. |
| **Data freshness** | Pure daily batch | Streaming + batch hybrid | **Hybrid** -- streaming (Kafka + Spark Streaming) makes features available ~5 hours earlier than a pure daily batch. Session-level attribution still requires daily batch (needs full session data). |

### Detailed Trade-off: Click-Only vs. Viewport Labels

```
Click-only:
  + Simple instrumentation (just log clicks)
  + Low data volume (~20M events/day vs 2B)
  + No IntersectionObserver complexity
  - 95% of impressions have no label (sparse)
  - Position bias undetectable (can't distinguish "not seen" from "seen but not clicked")
  - Model learns CTR, not relevance

Viewport (PBE):
  + Dense labels for every impression
  + Enables position bias correction (know what was seen)
  + Richer signal (dwell, engagement depth)
  - 100x more data volume to process
  - IntersectionObserver has mobile edge cases
  - More complex attribution pipeline
```

**Verdict**: The 100x data volume increase is justified by the qualitative
improvement in label quality. Sparse labels are the #1 bottleneck for ranking
model quality -- viewport data removes it.

### Detailed Trade-off: Daily Batch vs. Streaming

The hybrid approach uses streaming for features and batch for attribution:

| Aspect | Pure Batch | Pure Streaming | Hybrid (our choice) |
|--------|-----------|---------------|---------------------|
| Feature freshness | T+24h | T+5min | T+5min (streaming) |
| Attribution freshness | T+24h | T+5min | T+24h (batch) |
| Complexity | Low | High | Medium |
| Cost | Low | High | Medium |
| Session completeness | Full sessions | Partial sessions | Full sessions for attribution |

Attribution requires complete session data (a user might click 30 minutes after
seeing an item). Streaming attribution would produce partial, inaccurate labels.
The hybrid avoids this while still accelerating feature availability.
"""

# ---------------------------------------------------------------------------
# S7: Adversarial Defense Q&A
# ---------------------------------------------------------------------------

DEFENSE = r"""## Adversarial Defense Q&A

**Q: IntersectionObserver-based viewport tracking is known to be unreliable on mobile browsers. What is your actual accuracy?**

> **Limitation acknowledged:** Mobile viewport tracking has edge cases. iOS Safari
> delays IntersectionObserver callbacks during momentum scrolling, and some Android
> WebViews do not fire events during fling gestures.
>
> **Mitigation:** We supplement IntersectionObserver with a 200ms scroll-end polling
> fallback: when scrolling stops, we force-check all visible items. We also
> cross-validate viewport logs against server-side "above-the-fold" position
> heuristics (items at positions 1--4 are assumed 100% visible).
>
> **Data:** In an eye-tracking validation study (N=500 sessions), our viewport
> labels agreed with actual eye fixation data at 85% accuracy. The main error mode
> is fast scrolling (items scrolled past in <1s counted as "not exposed" but
> sometimes seen). This is a conservative error -- it under-counts exposure, which
> is safer than over-counting for training purposes.

---

**Q: Your IPW position bias correction requires randomization experiments. Does randomly reordering results hurt the user experience?**

> **Limitation acknowledged:** Yes, randomization degrades short-term UX for
> participating queries.
>
> **Mitigation:** We randomize only ~0.1% of queries (low user impact) and only
> swap items within a "quality tier" (items with similar relevance scores). We
> never put a truly irrelevant item at position 1. The randomization is also
> limited to non-sensitive verticals (not health/safety categories).
>
> **Data:** In the 0.1% randomized traffic, CTR drops ~15% compared to ranked
> traffic. But the IPW weights derived from this data improve model quality for the
> remaining 99.9% of traffic. Net impact: +1.8% NDCG improvement in the ranking
> model, translating to +0.5% site-wide GMV. The ROI of randomization is extremely
> positive.

---

**Q: 5-minute micro-batch latency for Stream 1 means your "near-real-time" claim is misleading. How does a 5-minute delay affect model quality?**

> **Limitation acknowledged:** 5 minutes is not real-time, and we do not use this
> data for online features.
>
> **Mitigation:** The 5-minute delay only affects offline feature aggregation. The
> training pipeline uses daily batch attribution anyway (requires full session
> data). The streaming layer's value is in making features available for the
> *next day's* training batch 5 hours earlier than a pure daily batch would. This
> accelerates the feedback loop from ~30 hours to ~25 hours.
>
> **Data:** Reducing the feedback loop from 30h to 25h improved model
> responsiveness to trend shifts (e.g., new product launches) by ~1 day,
> measurable in a 0.3% engagement lift on trending queries.

---

**Q: Multi-touch attribution sounds principled but adds significant complexity. Have you measured whether it actually outperforms last-touch?**

> **Limitation acknowledged:** Multi-touch attribution is harder to implement,
> debug, and explain to stakeholders.
>
> **Mitigation:** We ran a 4-week A/B test: models trained on multi-touch labels
> vs. last-touch labels, everything else equal.
>
> **Data:** Multi-touch model showed +0.8% NDCG improvement on organic results and
> +1.2% improvement on module-diverse queries (where items appeared in both organic
> and carousel). For single-module queries (item only in organic), the improvement
> was negligible (+0.1%). So multi-touch attribution pays off specifically for the
> increasingly common multi-module SRP layout, which validates the investment.
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline
# ---------------------------------------------------------------------------

VERBAL_OUTLINE = r"""## Verbal Outline

### 3-Minute Version

1. **(30s) Problem**: Click-based training data is sparse (2--5% CTR) and
   position-biased. 95% of impressions produce no training signal at all.

2. **(45s) Solution**: Viewport-based exposure tracking using
   IntersectionObserver, plus dual-stream ingestion -- behavioral events through
   Sojourner and product features through Kafka.

3. **(60s) Pipeline**: Trackable IDs injected server-side into every search
   result. IntersectionObserver fires viewport events. Sojourner stitches
   sessions. Spark Join resolves IDs at 5-min micro-batches. Attribution engine
   applies IPW position bias correction and multi-touch module credit. Output:
   Parquet training data partitioned by date and model version.

4. **(30s) Production scale**: 500M impressions/day, 2B viewport events/day,
   5-min micro-batch resolution, daily model retrain on 14-day attributed data
   window.

5. **(15s) Impact**: +1.8% NDCG improvement from IPW-debiased labels. Every
   ranking model at eBay trains on this pipeline's output.

### 10-Minute Version

1. **(1.5 min) Why clicks are not enough**: Sparsity (2--5% CTR means 95%+ of
   impressions have no label), position bias (top results get clicked regardless
   of quality), trust bias, and click != satisfaction (bounce-backs counted same
   as deep engagement).

2. **(2 min) Viewport tracking design**: IntersectionObserver API, threshold
   tuning ($\tau$ = 1s, visible_pct > 50%), mobile edge cases (iOS momentum
   scrolling workaround with 200ms polling fallback), eye-tracking validation
   study (85% accuracy, conservative error mode).

3. **(2 min) Dual-stream architecture**: Stream 1 -- behavioral events through
   Sojourner (200K events/sec) to Spark Join (5-min micro-batch for session + ID
   resolution). Stream 2 -- product features through Kafka Feature Broker (50K
   updates/sec) to Spark Streaming feature tables. Why two streams: behavioral
   events need session context, features are independently updatable.

4. **(1.5 min) Attribution deep dive**: IPW position bias correction -- estimated
   from 0.1% randomization experiments, monthly refresh, quality-tier-constrained
   randomization. Multi-touch module attribution -- exposure-weighted credit
   distribution across modules. Position-debiased LambdaMART training with
   IPW-weighted pairwise loss.

5. **(2 min) Production constraints**: Scale numbers (500M impressions, 2TB
   daily snapshots, 500-node Spark cluster, 4-hour daily attribution batch).
   Latency budget (<1ms trackable ID injection, async beacon firing, zero impact
   on search latency). 30-day retention with date partitioning.

6. **(1 min) Key lessons**: IPW randomization ROI is extremely positive (0.1%
   traffic cost for +1.8% NDCG). Multi-touch attribution only pays off for
   multi-module SRP layouts -- single-module queries see negligible improvement.
   Hybrid streaming+batch is the pragmatic middle ground (streaming for feature
   freshness, batch for attribution correctness).
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def populate_pbe_pipeline() -> None:
    """Find the pbe-pipeline SystemDesign record and populate all 8 sections."""
    init_db()
    db = SessionLocal()

    try:
        record = (
            db.query(SystemDesign)
            .filter(SystemDesign.slug == "pbe-pipeline")
            .first()
        )

        if record is None:
            print("[FAIL] No SystemDesign record found with slug='pbe-pipeline'.")
            print("       Run scripts/seed_system_designs.py first.")
            sys.exit(1)

        record.overview = OVERVIEW.strip()
        record.architecture = ARCHITECTURE.strip()
        record.dataflow = DATAFLOW.strip()
        record.formulas = FORMULAS.strip()
        record.production_constraints = PRODUCTION_CONSTRAINTS.strip()
        record.tradeoffs = TRADEOFFS.strip()
        record.defense = DEFENSE.strip()
        record.verbal_outline = VERBAL_OUTLINE.strip()

        db.commit()
        print(f"[DONE] Updated pbe-pipeline (id={record.id}) with all 8 sections.")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_pbe_pipeline()
